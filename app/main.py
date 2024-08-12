"""
main.py

FastAPI application for video processing and embedding management.
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
from app.models import PineconeCreds, QueryModel
from app.services.video_splitter import VideoSceneSplitter
from app.services.frame_extractor import VideoFrameExtractor
from app.services.final_reel_generator import FinalReelGenerator
from app.services.clip_pinecone import CLIPPineconeIntegration
from app.services.video_downloader import YouTubeVideoDownloader
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== NOTE: TO CHANGE SOON ======

# Directory paths
VIDEOS_DIR = "data/videos"
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

# Initialize VideoSceneSplitter and VideoFrameExtractor with default values
splitter = VideoSceneSplitter()
extractor = VideoFrameExtractor()
reel_generator = FinalReelGenerator()


class ReelData(BaseModel):
    video_clips: List[str]  # List of video clip URLs (blobs)
    script: str  # The sentence for which the clips are provided


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
        print(splitter.metadata)
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
        clip_pinecone = CLIPPineconeIntegration(
            api_key=creds.api_key, index_name=creds.index_name)
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
        clip_pinecone = CLIPPineconeIntegration(
            api_key=query.api_key, index_name=query.index_name)
        relevant_images = clip_pinecone.find_similar_images(
            query.query_sentence)
        return relevant_images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download_videos/")
async def download_videos(video_urls: List[str]):
    """
    Download multiple YouTube videos based on their URLs.
    """
    try:
        output_dir = os.path.dirname("./videos/")
        downloader = YouTubeVideoDownloader()

        for video_url in video_urls:
            downloader.download_youtube_video(video_url, output_dir)

        return {"message": "All videos downloaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/clips_for_script")
async def get_clips_for_script(
    api_key: str = Query(...),
    index_name: str = Query(...),
    script: str = Query(...)
):
    print("api_key: ", api_key)
    print("index_name: ", index_name)
    print("script: ", script)

    try:
        # Initialize the CLIPPineconeIntegration with the provided API key and index name
        clip_pinecone = CLIPPineconeIntegration(
            api_key=api_key, index_name=index_name
        )

        # Split the script into sentences
        sentences = script.split(". ")
        output_map = {}

        # Process each sentence to retrieve relevant video clips
        for sentence in sentences:
            relevant_images = clip_pinecone.find_similar_images(sentence)
            video_files = []

            # Convert each relevant image to the corresponding video clip path
            for image in relevant_images['matches']:
                image_path = image['metadata']['path']
                image_basename = os.path.basename(image_path)
                video_clip_name = image_basename.replace(
                    ".jpg", ".mp4").replace("f-", "")
                video_clip_path = os.path.join("data/clips", video_clip_name)

                if os.path.exists(video_clip_path):
                    video_files.append(video_clip_path)
                else:
                    raise HTTPException(status_code=404, detail=f"Video clip {
                                        video_clip_path} not found.")

            output_map[sentence] = video_files

        return output_map

    except Exception as e:
        # Raise an HTTP 500 error with the exception message if an error occurs
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create_reels/")
async def create_reels(reels_data: List[ReelData]):
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        final_videos = []

        for reel in reels_data:
            video_files = []
            for clip_path in reel.video_clips:
                # Construct full path to the clip
                full_path = os.path.join(root_dir, clip_path)
                if os.path.exists(full_path):
                    video_files.append(full_path)
                else:
                    return {"error": f"File not found: {full_path}"}

            script = reel.script

            # Call the create_reel function for each reel data item
            video_clip = reel_generator.create_reel(video_files, script)
            final_videos.append(video_clip)

        # Concatenate all clips into one final reel
        final_video_path = reel_generator.concatenate_all_clips(
            final_videos, "data/videos/final_reel.mp4")

        return {"message": "Reels created successfully!", "final_video_path": final_video_path}

    except Exception as e:
        return {"error": str(e)}


@app.get("/video_clip/")
async def serve_video_clip(file_path: str):
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4")
    else:
        raise HTTPException(status_code=404, detail="Video clip not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
