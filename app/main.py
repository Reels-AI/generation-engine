"""
main.py

FastAPI application for video processing and embedding management.
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Optional
from app.models import PineconeCreds, QueryModel
from app.services.video_splitter import VideoSceneSplitter
from app.services.frame_extractor import VideoFrameExtractor
from app.services.clip_pinecone import CLIPPineconeIntegration

app = FastAPI()

# ====== NOTE: TO CHANGE SOON ======

# Directory paths
VIDEOS_DIR = "data/videos"
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

# Initialize VideoSceneSplitter and VideoFrameExtractor with default values
splitter = VideoSceneSplitter()
extractor = VideoFrameExtractor()

@app.post("/clip_videos/")
async def clip_videos(video_files: List[UploadFile] = File(...), output_dir: Optional[str] = None):
    """
    Clip videos into scenes using adaptive thresholding.
    """
    try:
        for video_file in video_files:
            video_path = os.path.join(VIDEOS_DIR, video_file.filename)
            with open(video_path, "wb") as buffer:
                buffer.write(video_file.file.read())
        
        splitter.split_all_videos_in_directory(VIDEOS_DIR, output_dir)
        return {"message": "Videos clipped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract_images/")
async def extract_images():
    """
    Extract the first frame from all video clips and save them as images.
    """
    try:
        extractor.extract_all_first_frames()
        return {"message": "Frames extracted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/store_embeddings/")
async def store_embeddings(creds: PineconeCreds, image_dir: Optional[str] = None):
    """
    Store image embeddings in Pinecone.
    """
    try:
        clip_pinecone = CLIPPineconeIntegration(api_key=creds.api_key, index_name=creds.index_name)
        clip_pinecone.store_directory_images()
        return {"message": "Embeddings stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrieve_embeddings/")
async def retrieve_embeddings(query: QueryModel):
    """
    Retrieve relevant image embeddings from Pinecone based on a query sentence.
    """
    try:
        clip_pinecone = CLIPPineconeIntegration(api_key=query.api_key, index_name=query.index_name)
        relevant_images = clip_pinecone.find_similar_images(query.query_sentence)
        return relevant_images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)