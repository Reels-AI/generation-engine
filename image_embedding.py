import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import pinecone
import logging
import os
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Pinecone
from pinecone import Pinecone, ServerlessSpec

# Set your Pinecone API key
api_key = 'f045bc0a-d427-443c-a2be-b81fd2205e88'  # replace with your actual Pinecone API key

pc = Pinecone(api_key=api_key)

# Define the index name
index_name = 'dev-test-01'

# Check if the index already exists, if not, create it
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name, 
        dimension=512,  # assuming CLIP features are 512-dimensional
        metric='cosine',  # you can choose the metric according to your needs
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'  # replace with your preferred and available region
        )
    )

# Connect to the index
index = pc.Index(index_name)

# Load CLIP model and processor
model_name = "openai/clip-vit-base-patch32"
clip_model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)

def extract_image_features(image):
    """
    Extracts features from an image using the CLIP model.
    """
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    return image_features.squeeze().numpy()

def extract_text_features(text):
    """
    Extracts features from text using the CLIP model.
    """
    inputs = processor(text=text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_features = clip_model.get_text_features(**inputs)
    return text_features.squeeze().numpy()

def store_features_in_pinecone(index, id, features, metadata=None):
    """
    Stores features in a Pinecone index.
    """
    features_list = features.tolist()
    if metadata:
        index.upsert([(id, features_list, metadata)])
    else:
        index.upsert([(id, features_list)])

def query_pinecone(index, query_vector, top_k=None):
    """
    Queries Pinecone index with a vector and returns the most similar results.
    """
    results = index.query(vector=query_vector.tolist(), top_k=top_k, include_metadata=True)
    return results

def find_relevant_images(sentence, top_k=5):
    """
    Finds the most relevant images/embeddings in Pinecone given a sentence.
    """
    query_features = extract_text_features(sentence)
    query_features = query_features / np.linalg.norm(query_features)
    results = query_pinecone(index, query_features, top_k)
    return results

if __name__ == "__main__":
    # Example usage: Store image features
    image_path = 'frames/f-video-s-002.jpg'
    image = Image.open(image_path)
    image_features = extract_image_features(image)
    store_features_in_pinecone(index, 'image-1', image_features, {"path": image_path})
    logging.info("Image features stored successfully in Pinecone.")

    # Example usage: Query with a sentence
    query_sentence = "A person standing in front of a building"
    relevant_images = find_relevant_images(query_sentence)
    
    logging.info(f"Most relevant images for '{query_sentence}':")
    for match in relevant_images['matches']:
        log_message = f"ID: {match['id']}, Score: {match['score']}"
        if 'metadata' in match:
            log_message += f", Metadata: {match['metadata']}"
        logging.info(log_message)