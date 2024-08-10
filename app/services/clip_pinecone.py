"""
Store and Retrieve Relevant Image Embeddings

This class provides functionality to extract features from images and text using CLIP,
store these features in a Pinecone index, and perform similarity searches.
"""

import os
from typing import List, Dict, Union, Optional
import numpy as np
import torch
from PIL import Image
from pinecone import Pinecone, ServerlessSpec
from transformers import CLIPProcessor, CLIPModel
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CLIPPineconeIntegration:
    def __init__(self, api_key: str, index_name: str, model_name: str = "openai/clip-vit-base-patch32", default_image_dir: str = "data/frames"):
        """
        Initialize the CLIP-Pinecone integration.

        Args:
            api_key (str): Pinecone API key.
            index_name (str): Name of the Pinecone index.
            model_name (str): Name of the CLIP model to use.
            default_image_dir (str): Default directory to fetch images from.
        """
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.default_image_dir = default_image_dir
        self._initialize_index()
        self.index = self.pc.Index(self.index_name)
        
        self.clip_model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def _initialize_index(self):
        """Initialize the Pinecone index if it doesn't exist."""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=512,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            logger.info(f"Created new Pinecone index: {self.index_name}")

    def extract_image_features(self, image: Image.Image) -> np.ndarray:
        """
        Extract features from an image using the CLIP model.

        Args:
            image (PIL.Image.Image): The input image.

        Returns:
            np.ndarray: The extracted image features.
        """
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
        return image_features.squeeze().numpy()

    def extract_text_features(self, text: str) -> np.ndarray:
        """
        Extract features from text using the CLIP model.

        Args:
            text (str): The input text.

        Returns:
            np.ndarray: The extracted text features.
        """
        inputs = self.processor(text=text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            text_features = self.clip_model.get_text_features(**inputs)
        return text_features.squeeze().numpy()

    def store_features(self, id: str, features: np.ndarray, metadata: Optional[Dict] = None) -> bool:
        """
        Store features in the Pinecone index.

        Args:
            id (str): The unique identifier for the vector.
            features (np.ndarray): The feature vector to store.
            metadata (Dict, optional): Additional metadata to store with the vector.

        Returns:
            bool: True if a new vector was inserted, False if the vector already existed.
        """
        features_list = features.tolist()

        if metadata:
            self.index.upsert([(id, features_list, metadata)])
        else:
            self.index.upsert([(id, features_list)])
        logger.info(f"Vector with ID {id} has been inserted into Pinecone.")

        return True


    def find_similar_images(self, query: str, top_k: int = 5) -> Dict:
        """
        Find the most relevant images in Pinecone given a text query.

        Args:
            query (str): The input text query.
            top_k (int): The number of top results to return.

        Returns:
            Dict: The query results from Pinecone in a serializable format.
        """
        query_features = self.extract_text_features(query)
        query_features = query_features / np.linalg.norm(query_features)
        
        results = self.index.query(
            vector=query_features.tolist(),
            top_k=top_k,
            include_metadata=True,
            filter={"type": "image"}
        )
        
        # Convert the results to a serializable format
        serializable_results = {
            "matches": [
                {
                    "id": match["id"],
                    "score": float(match["score"]),  # Ensure score is a Python float
                    "metadata": match.get("metadata", {})
                }
                for match in results["matches"]
            ]
        }
        
        return serializable_results
    
    def store_directory_images(self, directory_path: Optional[str] = None) -> None:
        """
        Store features of all images in a given directory to Pinecone.

        Args:
            directory_path (str, optional): Path to the directory containing images.
                                            If not provided, uses the default image directory.
        """
        directory_path = directory_path or self.default_image_dir
        
        if not os.path.isdir(directory_path):
            logger.error(f"Directory {directory_path} does not exist.")
            return
        
        logger.info(f"Processing images from directory: {directory_path}")

        metadata_file_path = os.path.join('data', 'clips', 'metadata.json')

        with open(metadata_file_path, 'r') as f:
            main_metadata = json.load(f)
            
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join(directory_path, filename)
                try:
                    image = Image.open(image_path)
                    image_features = self.extract_image_features(image)
                    image_id = f"image-{filename}"
                    # metadata = {"path": image_path, "type": "image"}
                    was_inserted = self.store_features(image_id, image_features, metadata)
                    if was_inserted:
                        logger.info(f"Stored features for {filename}")
                    else:
                        logger.info(f"Features for {filename} already existed")
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")

    def delete_all_embeddings(self) -> None:
        """Delete all embeddings from the Pinecone index."""
        try:
            index_stats = self.index.describe_index_stats()
            total_vector_count = index_stats['total_vector_count']

            if total_vector_count == 0:
                logger.info("The index is already empty.")
                return

            self.index.delete(delete_all=True)
            logger.info(f"All {total_vector_count} embeddings have been deleted from the Pinecone index.")
        except Exception as e:
            logger.error(f"An error occurred while trying to delete all embeddings: {str(e)}")

# Example usage
# if __name__ == "__main__":
#     api_key = '$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
#     index_name = 'ENTER'
    
#     clip_pinecone = CLIPPineconeIntegration(api_key, index_name)
    
#     # Store images from a directory
#     image_directory = 'frames'
#     clip_pinecone.store_directory_images(image_directory)
    
#     # Query for similar images
#     query_sentence = "A robot in a laboratory"
#     relevant_images = clip_pinecone.find_similar_images(query_sentence)
    
#     logger.info(f"Most relevant images for '{query_sentence}':")
#     for match in relevant_images['matches']:
#         log_message = f"ID: {match['id']}, Score: {match['score']}"
#         if 'metadata' in match:
#             log_message += f", Metadata: {match['metadata']}"
#         logger.info(log_message)
    
#     # Optionally, delete all embeddings
#     # clip_pinecone.delete_all_embeddings()