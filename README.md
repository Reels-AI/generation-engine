# Generation Engine

Reelsai.me video generation engine

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- Clip videos into scenes using adaptive thresholding.
- Extract the first frame from video clips and save them as images.
- Store image embeddings in Pinecone.
- Retrieve relevant image embeddings based on a text query.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/generation-engine.git
   cd generation-engine

2. Create a virtual environment:
```bash
python -m venv env
source env/bin/activate
```
3. Install packages:

```bash
pip install -r requirements.txt
```
4. Set up environment variables:
```bash
export PINECONE_API_KEY='your_pinecone_api_key'
export PINECONE_INDEX_NAME='your_index_name'
```

## Usage

1. Start the FastAPI server:
```bash
python -m app.main
```
2. Access the API documentation at http://localhost:8000/docs to explore the available endpoints.

## API Endpoints

1. Clip Videos
```http
POST /clip_videos/
```
Description: Clips videos into scenes using adaptive thresholding.
Request: Upload video files.
Response: Confirmation message.

2. Extract Images
```http
POST /extract_images/
```
Description: Extracts the first frame from all video clips and saves them as images.
Response: Confirmation message.

3. Store Embeddings
```http
POST /store_embeddings/
```
Description: Stores image embeddings in Pinecone.
Request: JSON body with creds (API key and index name) and optional image_dir.
Response: Confirmation message.

4. Retrieve Embeddings
```http
POST /retrieve_embeddings/
```
Description: Retrieves relevant image embeddings from Pinecone based on a query sentence.
Request: JSON body with api_key, index_name, and query_sentence.
Response: List of relevant images.

## Project Structure

```
generation-engine/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── services/
│       ├── video_splitter.py
│       ├── frame_extractor.py
│       └── clip_pinecone.py
│
├── tests/
│   ├── ping.py
│
├── data/
│   ├── videos/
│   ├── clips/
│   └── frames/
│
├── requirements.txt
├── README.md
└── .gitignore
```
<!-- 
generation-engine/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── config.py
│   └── services/
│       ├── __init__.py
│       ├── video_splitter.py
│       ├── frame_extractor.py
│       └── clip_pinecone.py
│
├── tests/
│   ├── __init__.py
│   ├── test_clip_videos.py
│   ├── test_extract_images.py
│   ├── test_store_embeddings.py
│   └── test_retrieve_embeddings.py
│
├── data/
│   ├── videos/
│   ├── clips/
│   └── frames/
│
├── requirements.txt
├── README.md
└── .gitignore -->