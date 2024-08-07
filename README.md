# Generation Engine

This FastAPI application provides functionality for video processing, including clipping videos into scenes, extracting frames, and managing image embeddings using Pinecone and CLIP.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
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