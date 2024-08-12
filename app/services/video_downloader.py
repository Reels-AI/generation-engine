import yt_dlp
import os
import logging
import uuid
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeVideoDownloader:
    def __init__(self, default_output_dir: str = 'videos'):
        """
        Initialize the YouTubeVideoDownloader.

        Args:
            default_output_dir (str): Default directory where the downloaded videos will be saved.
        """
        # Set the root directory to the project's root
        self.root_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        self.default_output_dir = os.path.join(
            self.root_dir, default_output_dir)

        if not os.path.exists(self.default_output_dir):
            os.makedirs(self.default_output_dir)
            logger.info(f"Created default output directory: {
                        self.default_output_dir}")

    def download_youtube_video(self, url: str, output_path: Optional[str] = None) -> None:
        """
        Download a YouTube video to the specified output directory.

        Args:
            url (str): The URL of the YouTube video to download.
            output_path (Optional[str]): The directory where the video will be saved.
        """
        try:
            # Use default output directory if none is provided
            if output_path is None:
                output_path = self.default_output_dir

            # Ensure the output directory exists
            os.makedirs(output_path, exist_ok=True)

            # Generate a unique filename using UUID
            unique_id = uuid.uuid4().hex
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/bestvideo[height<=720]+bestaudio/best',
                'outtmpl': os.path.join(output_path, f'{unique_id}.%(ext)s'),
                'merge_output_format': 'mp4',  # Ensure the final output is in mp4 format
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            logger.info(f"Downloaded video with ID {
                        unique_id} to {output_path}")

        except Exception as e:
            logger.error(f"An error occurred while downloading the video: {e}")


# Example usage
# if __name__ == "__main__":
#     youtube_link = "https://www.youtube.com/watch?v=yJucBMuHys8"
#     downloader = YouTubeVideoDownloader()
#     downloader.download_youtube_video(youtube_link)
