import os
import logging
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def split_adaptive_video(video_path, output_path=None, stats_file_name=None, output_file_template='$VIDEO_NAME-s-$SCENE_NUMBER.mp4'):
    """
    Splits a video into scenes using adaptive thresholding.

    Parameters:
    video_path (str): Path to the input video file.
    output_path (str): Path to the directory where the split video scenes will be saved.
    stats_file_path (str): Path to the file where scene detection statistics will be saved.
    output_file_template (str): Template for naming the output video files.
    """
    try:
        # Detect scenes using adaptive thresholding
        if not os.path.exists('stats/') and stats_file_name:
            os.makedirs('stats/')
            stats_file_path = os.path.join('stats/', stats_file_name)

        scene_list = detect(video_path, AdaptiveDetector(), stats_file_path)
        logging.info(f"Detected {len(scene_list)} scenes in {video_path}")

        # Split video into scenes
        split_video_ffmpeg(video_path, scene_list, output_path, output_file_template)
        logging.info(f"Video split into scenes and saved to {output_path}")

    except Exception as e:
        logging.error(f"An error occurred while splitting the video: {e}")

# Example usage:
# split_adaptive_video('video.mp4', 'clips', 'stats.csv')