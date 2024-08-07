"""
Video Frame Extractor

This class provides functionality to extract the first frame from video files and save them as images.
"""

import os
import logging
from typing import Optional
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoFrameExtractor:
    def __init__(self, clips_dir: str = 'data/clips' , output_dir: str = 'data/frames'):
        """
        Initialize the VideoFrameExtractor.

        Args:
            clips_dir (str, optional): Directory containing the .mp4 video files. Defaults to 'clips'.
            output_dir (str, optional): Directory where the extracted frames will be saved. Defaults to 'frames'.
        """
        if not os.path.exists(clips_dir):
            logger.error(f"Video clips directory does not exist: {clips_dir}")
            return

        self.clips_dir = clips_dir
        self.output_dir = output_dir

        # Ensure the output directory exists
        # os.makedirs(self.output_dir, exist_ok=True)

    def extract_first_frame(self, video_path: str, output_image_path: str) -> Optional[str]:
        """
        Extracts the first frame from a video file and saves it as an image.

        Args:
            video_path (str): Path to the video file.
            output_image_path (str): Path where the extracted frame will be saved as an image.

        Returns:
            Optional[str]: Path to the saved image if successful, None otherwise.
        """
        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Check if the video was opened successfully
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return None

        # Read the first frame
        ret, frame = cap.read()

        # Check if the frame was read successfully
        if not ret:
            logger.error(f"Could not read frame from video: {video_path}")
            cap.release()
            return None

        # Save the frame as an image file
        success = cv2.imwrite(output_image_path, frame)
        if success:
            logger.info(f"First frame extracted and saved to {output_image_path}")
            cap.release()
            return output_image_path
        else:
            logger.error(f"Failed to save the frame to {output_image_path}")
            cap.release()
            return None

    def extract_all_first_frames(self) -> None:
        """
        Extracts the first frame from all .mp4 videos in the specified directory and saves them as images.
        """
        # Check if the clips directory exists
        if not os.path.exists(self.clips_dir):
            logger.error(f"Video clips directory does not exist: {self.clips_dir}")
            return

        # Get the list of .mp4 files in the clips directory
        videos = [file for file in os.listdir(self.clips_dir) if file.lower().endswith('.mp4')]

        if not videos:
            logger.warning(f"No .mp4 files found in directory: {self.clips_dir}")
            return

        # Create the output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")

        for video in videos:
            video_path = os.path.join(self.clips_dir, video)
            output_image_path = os.path.join(self.output_dir, f'f-{os.path.splitext(video)[0]}.jpg')

            self.extract_first_frame(video_path, output_image_path)

# Example usage
# if __name__ == "__main__":
#     clips_directory = 'clips'
#     frames_directory = 'frames'
    
#     extractor = VideoFrameExtractor(clips_directory, frames_directory)
#     extractor.extract_all_first_frames()