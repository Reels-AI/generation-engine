"""
Video Clips Generation

This class provides functionality to detect scenes in a video using adaptive thresholding
and split the video into scenes.
"""

import os
import re
import logging
from typing import Optional
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from moviepy.editor import *
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoSceneSplitter:
    def __init__(self, stats_dir: str = 'data/stats', default_output_dir: str = 'data/clips'):
        """
        Initialize the VideoSceneSplitter.

        Args:
            stats_dir (str): Directory where scene detection statistics will be saved.
            default_output_dir (str): Default directory where the split video scenes will be saved.
        """
        self.stats_dir = stats_dir
        self.default_output_dir = default_output_dir
        self.metadata = {}

        # if not os.path.exists(self.stats_dir):
        #     os.makedirs(self.stats_dir)
        #     logger.info(f"Created stats directory: {self.stats_dir}")

        if not os.path.exists(self.default_output_dir):
            os.makedirs(self.default_output_dir)
            logger.info(f"Created default output directory: {self.default_output_dir}")

    def split_adaptive_video(self, video_path: str, output_path: Optional[str] = None, stats_file_name: Optional[str] = None, output_file_template: str = '$VIDEO_NAME-s-$SCENE_NUMBER.mp4') -> None:
        """
        Splits a video into scenes using adaptive thresholding.

        Args:
            video_path (str): Path to the input video file.
            output_path (Optional[str]): Path to the directory where the split video scenes will be saved.
            stats_file_name (Optional[str]): Name of the file where scene detection statistics will be saved.
            output_file_template (str): Template for naming the output video files.
        """
        try:
            # stats_file_path = None
            # if stats_file_name:
            #     stats_file_path = os.path.join(self.stats_dir, stats_file_name)

            # Detect scenes using adaptive thresholding
            scene_list = detect(video_path, AdaptiveDetector())
            logger.info(f"Detected {len(scene_list)} scenes in {video_path}")

            # Use default output directory if none is provided
            if output_path is None:
                output_path = self.default_output_dir

            # Ensure the output directory exists
            os.makedirs(output_path, exist_ok=True)

            # Split video into scenes
            split_video_ffmpeg(video_path, scene_list, output_path, output_file_template)
            logger.info(f"Video split into scenes and saved to {output_path}")

        except Exception as e:
            logger.error(f"An error occurred while splitting the video: {e}")

    def split_all_videos_in_directory(self, videos_dir: str, output_dir: Optional[str] = None, stats_file_name: Optional[str] = None, output_file_template: str = '$VIDEO_NAME-s-$SCENE_NUMBER.mp4') -> None:
        """
        Splits all videos in a directory into scenes using adaptive thresholding.

        Args:
            videos_dir (str): Directory containing the video files.
            output_dir (Optional[str]): Directory where the split video scenes will be saved.
            stats_file_name (Optional[str]): Name of the file where scene detection statistics will be saved.
            output_file_template (str): Template for naming the output video files.
        """
        if not os.path.exists(videos_dir):
            logger.error(f"Video clips directory does not exist: {videos_dir}")
            return

        videos = [file for file in os.listdir(videos_dir) if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

        if not videos:
            logger.warning(f"No video files found in directory: {videos_dir}")
            return

        for video in videos:
            video_path = os.path.join(videos_dir, video)
            video_output_dir = output_dir if output_dir else self.default_output_dir
            video_stats_file_name = stats_file_name if stats_file_name else f"{os.path.splitext(video)[0]}_stats.csv"
            
            self.split_adaptive_video(video_path, video_output_dir, video_stats_file_name, output_file_template)
        
        self.clip_duration(video_output_dir)
    
    def clip_duration(self, videos_dir: str, metadata_file: str = 'metadata.json') -> None:
            """
            Calculate and return the duration of each video clip in the specified directory.

            Args:
                videos_dir (str): Directory containing the video clips.

            Returns:
                list: A list of tuples containing the file name and duration (in seconds) for each video clip.
            """
            if not os.path.exists(videos_dir):
                logger.error(f"Video directory does not exist: {videos_dir}")
                return []

            clips = [file for file in os.listdir(videos_dir) if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

            for clip in clips:
                clip_path = os.path.join(videos_dir, clip)
                clip_name = os.path.splitext(clip)[0]
                match = re.search(r's-(\d+)', clip)
                sequence = int(match.group(1)) if match else None

                try:
                    with VideoFileClip(clip_path) as video_clip:
                        duration = video_clip.duration
                        self.metadata[clip] = {"duration":duration, "sequence":sequence}
                        logger.info(f"Duration of {clip}: {duration} seconds")
                except Exception as e:
                    logger.error(f"An error occurred while processing {clip}: {e}")
            
            metadata_path = os.path.join(videos_dir, metadata_file)
            with open(metadata_path, 'w') as json_file:
                json.dump(self.metadata, json_file, indent=4)
            logger.info(f"Metadata saved to {metadata_path}")
            
# Example usage

# data/videos/ all the videos will be clipped and stored in data/clips/ by default.


# if __name__ == "__main__":
#     print('hello')
#     base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
#     videos_directory = os.path.join(base_dir, 'data', 'videos')
# #     stats_file_name = 'stats.csv'
    
#     splitter = VideoSceneSplitter()
#     splitter.split_all_videos_in_directory(videos_directory)
#     print(splitter.metadata)

