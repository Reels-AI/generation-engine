import cv2
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_first_frame(video_path, output_image_path):
    """
    Extracts the first frame from a video file and saves it as an image.

    Parameters:
    video_path (str): Path to the video file.
    output_image_path (str): Path where the extracted frame will be saved as an image.
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video was opened successfully
    if not cap.isOpened():
        logging.error(f"Could not open video: {video_path}")
        return
    
    # Read the first frame
    ret, frame = cap.read()
    
    # Check if the frame was read successfully
    if not ret:
        logging.error(f"Could not read frame from video: {video_path}")
        cap.release()
        return
    
    # Save the frame as an image file
    success = cv2.imwrite(output_image_path, frame)
    if success:
        logging.info(f"First frame extracted and saved to {output_image_path}")
    else:
        logging.error(f"Failed to save the frame to {output_image_path}")
    
    # Release the video capture object
    cap.release()

def extract_all_first_frames(videos_dir, output_dir):
    """
    Extracts the first frame from all .mp4 videos in a directory and saves them as images.

    Parameters:
    videos_dir (str): Directory containing the .mp4 video files.
    output_dir (str): Directory where the extracted frames will be saved.
    """
    # Check if the videos directory exists
    if not os.path.exists(videos_dir):
        logging.error(f"Video clips directory does not exist: {videos_dir}")
        return

    # Get the list of .mp4 files in the videos directory
    videos = [file for file in os.listdir(videos_dir) if file.endswith('.mp4')]

    if not videos:
        logging.warning(f"No .mp4 files found in directory: {videos_dir}")
        return
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

    for video in videos:
        video_path = os.path.join(videos_dir, video)
        output_image_path = os.path.join(output_dir, f'f-{os.path.splitext(video)[0]}.jpg')
        
        extract_first_frame(video_path, output_image_path)

# Example usage:
# extract_all_first_frames('clips/', 'frames/')
