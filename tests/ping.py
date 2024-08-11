import requests
import os
import json

# ===== ENVIRONMENT VARIABLES =====
SERVER_URL = "http://localhost:8000"
VIDEO_PATH = "../videos/video.mp4"
VIDEO_FOLDER_PATH = "../videos"
PINECONE_API_KEY = "f045bc0a-d427-443c-a2be-b81fd2205e88"
PINECONE_INDEX_NAME = "dev-test-04"
# Optional: (if not provided, it will use FRAMES_DIR from the server)
IMAGE_DIR = 'frames'


def test_clip_videos():
    # Iterate over all files in the folder
    for filename in os.listdir(VIDEO_FOLDER_PATH):
        if filename.endswith(".mp4"):
            video_path = os.path.join(VIDEO_FOLDER_PATH, filename)
            with open(video_path, "rb") as video_file:
                files = {"video_files": (os.path.basename(
                    video_path), video_file, "video/mp4")}
                response = requests.post(
                    f"{SERVER_URL}/clip_videos/", files=files)

            if response.status_code == 200:
                print(f"Response for {filename}:")
                print("Response status code:", response.status_code)
                print("Response content:", response.json())
            else:
                print(f"Error for {filename}: {response.status_code}")
                print(response.text)


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


def test_download_video(youtube_url):
    # Extract the directory from VIDEO_PATH
    output_dir = os.path.dirname(VIDEO_PATH)

    # Send video_url as a query parameter
    params = {
        "video_url": youtube_url
    }

    # Send output_dir as part of the JSON payload
    payload = {
        "output_dir": output_dir
    }

    response = requests.post(
        f"{SERVER_URL}/download_video/",
        params=params,
        json=payload
    )

    if response.status_code == 200:
        print("Response status code:", response.status_code)
        print("Response content:", response.json())
    else:
        print("Error:", response.status_code, response.text)


def test_retrieve_clips_for_script(script_text):
    payload = {
        "api_key": PINECONE_API_KEY,
        "index_name": PINECONE_INDEX_NAME,
        "script": script_text
    }

    response = requests.get(
        f"{SERVER_URL}/clips_for_script/",
        params=payload
    )

    if response.status_code == 200:
        print("Response status code:", response.status_code)
        print("Response content:", json.dumps(response.json(), indent=2))
    else:
        print("Error:", response.status_code, response.text)


if __name__ == "__main__":
    # test_download_video("https://www.youtube.com/watch?v=xj1SlU7Tyo0")
    # test_download_video("https://www.youtube.com/watch?v=oJySuIRWQIk")
    # test_download_video("https://www.youtube.com/watch?v=Ec9-5LkSzvI")
    # test_download_video("https://www.youtube.com/watch?v=yYpQvo1Et_k")
    # test_clip_videos()
    # test_extract_images()
    test_store_embeddings()
    # test_retrieve_embeddings("Hello man walking")
    # test_retrieve_clips_for_script("This is Kevin Piette, carrying the Olympic torch ahead of the opening ceremony of the Olympics earlier this week.  Having been in an accident 11 years ago that left him paraplegic, he's returned to tennis as a para-athlete. In this clip, he is seen using Atlante X an exoskeleton designed by Wandercraft that enables patients with upper extremity dysfunction or cognitive challenges to stand up and walk hands-free. As one of the first users of this exoskeleton, he has contributed to its improvement, igniting the future and showcasing the power of the human spirit and cutting-edge exoskeleton technology!")

    # {'sentence 1' : [clip_id_1, clip_id_2, ...], 'sentence 2' : [clip_id_1, clip_id_2, ...], ...}
