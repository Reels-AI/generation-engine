import requests
import os
import json

# ===== ENVIRONMENT VARIABLES =====
SERVER_URL = "http://localhost:8000"
VIDEO_PATH = "../videos/video.mp4"
PINECONE_API_KEY = "f045bc0a-d427-443c-a2be-b81fd2205e88"
PINECONE_INDEX_NAME = "dev-test-02"
IMAGE_DIR = 'frames' # Optional: (if not provided, it will use FRAMES_DIR from the server)

def test_clip_videos():

    with open(VIDEO_PATH, "rb") as video_file:
        files = {"video_files": (os.path.basename(VIDEO_PATH), video_file, "video/mp4")}
        response = requests.post(f"{SERVER_URL}/clip_videos/", files=files)
    
    if response.    status_code == 200:
        print("Response status code:", response.status_code)
        print("Response content:", response.json())
    else:
        print("Error:", response.status_code, response.text)

def test_extract_images():

    response = requests.post(f"{SERVER_URL}/extract_images/")
    
    if response.status_code == 200:
        print("Response status code:", response.status_code)
        print("Response content:", response.json())
    else:
        print("Error:", response.status_code, response.text)

def test_store_embeddings():

    payload = {
        "api_key": PINECONE_API_KEY,
        "index_name": PINECONE_INDEX_NAME
    }
    if IMAGE_DIR:
        payload["image_dir"] = IMAGE_DIR

    response = requests.post(
        f"{SERVER_URL}/store_embeddings/",
        json=payload
    )

    if response.status_code == 200:
        print("Response status code:", response.status_code)
        print("Response content:", response.json())
    else:
        print("Error:", response.status_code, response.text)

def test_retrieve_embeddings(query_sentence):

    payload = {
        "api_key": PINECONE_API_KEY,
        "index_name": PINECONE_INDEX_NAME,
        "query_sentence": query_sentence
    }

    response = requests.post(
        f"{SERVER_URL}/retrieve_embeddings/",
        json=payload
    )
    
    if response.status_code == 200:
        print("Response status code:", response.status_code)
        print("Response content:", json.dumps(response.json(), indent=2))
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    # test_clip_videos()
    # test_extract_images()
    # test_store_embeddings()
    test_retrieve_embeddings("Hello man walking")

    # {'sentence 1' : [clip_id_1, clip_id_2, ...], 'sentence 2' : [clip_id_1, clip_id_2, ...], ...}