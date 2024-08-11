import os
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoClip
from tempfile import NamedTemporaryFile
from typing import List, Optional, Tuple
from .google_text_to_speech import GoogleCloudAudioProcessor
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinalReelGenerator:
    def __init__(self, default_output_dir: str = 'reels'):
        """
        Initialize the VideoReelCreator.

        Args:
            default_output_dir (str): Default directory where the generated reels will be saved.
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

        self.audio_processor = GoogleCloudAudioProcessor()

    def create_reel(self, video_clips: List[str], script: str, output_path: Optional[str] = None) -> VideoClip:
        """
        Create a reel using an array of video clips and an audio file.

        Args:
            video_clips (List[str]): List of paths to video clips.
            script (str): Script to generate TTS audio.
            output_path (Optional[str]): Path to save the final reel.
        """
        try:
            # Generate the TTS audio content
            audio_content = self.audio_processor.generate_google_tts_audio(
                script)
            word_timings = self.audio_processor.transcribe_audio_with_timestamps(
                audio_content, script)
            if not audio_content:
                raise ValueError("Failed to generate TTS audio.")

            # Save the audio content to a temporary file
            with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                temp_audio_file.write(audio_content)
                temp_audio_file_path = temp_audio_file.name

            # Load the audio file
            audio = AudioFileClip(temp_audio_file_path)
            audio_duration = audio.duration

            # Load the video clips
            clips = [VideoFileClip(clip) for clip in video_clips]

            # Create the reel
            reel_clips = []
            current_duration = 0

            for clip in clips:
                clip_duration = clip.duration

                if current_duration + clip_duration > audio_duration:
                    # Cut the last clip to fit the audio duration
                    remaining_duration = audio_duration - current_duration
                    reel_clips.append(clip.subclip(0, remaining_duration))
                    current_duration += remaining_duration
                    break
                else:
                    reel_clips.append(clip)
                    current_duration += clip_duration

            # Concatenate the video clips into a single video
            final_reel = concatenate_videoclips(reel_clips)

            # Set the audio to the video
            final_reel = final_reel.set_audio(audio)

            # Use default output directory if none is provided
            if output_path is None:
                output_path = os.path.join(
                    self.default_output_dir, 'final_reel.mp4')

            # Write the final reel to a temporary file
            with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_reel_file:
                temp_reel_file_path = temp_reel_file.name
                final_reel.write_videofile(
                    temp_reel_file_path, codec="libx264", audio_codec="aac")

            # Add captions to the final reel
            captioned_clip = self.add_captions_to_video(
                temp_reel_file_path, word_timings)

            logger.info(f"Reel created successfully")
            return captioned_clip

        except Exception as e:
            logger.error(f"An error occurred while creating the reel: {e}")

        finally:
            # Clean up the temporary files
            if os.path.exists(temp_audio_file_path):
                os.remove(temp_audio_file_path)
            if os.path.exists(temp_reel_file_path):
                os.remove(temp_reel_file_path)

    def add_captions_to_video(self, video_path, word_timings, font='Roboto-Bold.ttf', fontsize=20, color='white', highlight_color='yellow', fps=24):
        """
        Adds captions to an existing video using the provided word timings.

        Parameters:
        - video_path: Path to the input video file.
        - word_timings: List of tuples with the format (word, start_time, end_time).
        - font: Font to use for the captions.
        - fontsize: Font size of the captions.
        - color: Color of the caption text.
        - highlight_color: Color of the highlighted word text.
        - fps: Frames per second for the output video.
        """

        video = VideoFileClip(video_path)
        frame_size = video.size

        # Load font
        try:
            font = ImageFont.truetype(font, fontsize)
        except OSError:
            font = ImageFont.load_default()
            print("Using default font as the specified font was not found.")

        all_words = [word for word, start, end in word_timings]
        full_text = ' '.join(all_words)

        # Calculate the maximum width for text (video width - 50 pixels)
        max_text_width = frame_size[0] - 50

        # Function to wrap text dynamically based on the maximum width
        def wrap_text(text, font, max_width):
            words = text.split(' ')
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                test_width = font.getbbox(test_line)[2]

                if test_width <= max_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]

            lines.append(' '.join(current_line))
            return '\n'.join(lines)

        # Wrap the text according to the calculated width
        wrapped_text = wrap_text(full_text, font, max_text_width)

        def make_frame(t):
            # Get the current frame from the original video
            frame = video.get_frame(t)
            img = Image.fromarray(frame)
            draw = ImageDraw.Draw(img)

            # Determine the current word based on the timing
            current_word = None
            for word, start, end in word_timings:
                if start <= t < end:
                    current_word = word
                    break

            # Calculate text size and position to align the text at the bottom
            lines = wrapped_text.split('\n')
            text_height = sum([font.getbbox(line)[3] for line in lines]) + \
                10 * (len(lines) - 1)  # Adding line spacing
            # 25 pixels margin on both sides and 20 pixels from the bottom
            text_position = (25, frame_size[1] - text_height - 20)

            # Draw the full text
            y_position = text_position[1]
            for line in lines:
                draw.text((text_position[0], y_position),
                          line, font=font, fill=color)
                # Move to the next line with spacing
                y_position += font.getbbox(line)[3] + 10

            # Highlight the current word
            if current_word:
                current_x = text_position[0]
                current_y = text_position[1]

                for line in lines:
                    words = line.split(' ')
                    for word in words:
                        word_width = font.getbbox(word)[2]
                        if word == current_word:
                            draw.text((current_x, current_y), word,
                                      font=font, fill=highlight_color)
                        current_x += word_width + font.getbbox(' ')[2]

                    # Move to the next line
                    current_x = text_position[0]
                    # Move to the next line with spacing
                    current_y += font.getbbox(line)[3] + 10

            return np.array(img)

        # Generate a video with captions overlayed on the original video frames
        captioned_clip = VideoClip(
            make_frame, duration=video.duration).set_audio(video.audio)
        captioned_clip.fps = fps

        return captioned_clip

    def prepare_clip(self, clip: VideoFileClip, target_fps: int, target_resolution: Tuple[int, int]) -> VideoFileClip:
        """
        Prepare a clip by setting its frame rate and resizing it to a target resolution.

        Args:
            clip (VideoFileClip): The original video clip.
            target_fps (int): The target frame rate.
            target_resolution (Tuple[int, int]): The target resolution (width, height).

        Returns:
            VideoFileClip: The prepared video clip.
        """
        return clip.set_fps(target_fps).resize(target_resolution)

    def concatenate_all_clips(self, video_clips: List[VideoClip], output_path: Optional[str] = None) -> str:
        """
        Concatenate all video clips into a single video.

        Args:
            video_clips (List[VideoClip]): List of VideoClip objects.
            output_path (Optional[str]): Path to save the final reel.

        Returns:
            str: Path to the saved final video file.
        """
        try:
            target_fps = 24
            target_resolution = (1920, 1080)

            # Ensure all clips have the same frame rate and resolution
            clips = [self.prepare_clip(clip, target_fps, target_resolution)
                     for clip in video_clips]

            # Concatenate the video clips into a single video
            final_reel = concatenate_videoclips(clips, method="compose")

            # Use default output directory if none is provided
            if output_path is None:
                output_path = os.path.join(
                    self.default_output_dir, 'final_reel.mp4')

            # Write the final reel to the specified output file
            final_reel.write_videofile(
                output_path, codec="libx264", audio_codec="aac")

            logger.info(f"Reel created successfully at {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"An error occurred while creating the reel: {e}")
            raise e


# Example usage
if __name__ == "__main__":
    video_clips = ["3296848768a94c5e8d43a7507f07e67b-s-001.mp4",
                   "3296848768a94c5e8d43a7507f07e67b-s-002.mp4", "3296848768a94c5e8d43a7507f07e67b-s-003.mp4", "3296848768a94c5e8d43a7507f07e67b-s-004.mp4",
                   "3296848768a94c5e8d43a7507f07e67b-s-005.mp4", "3296848768a94c5e8d43a7507f07e67b-s-006.mp4", "3296848768a94c5e8d43a7507f07e67b-s-007.mp4",]
    script = "This is a sample script for the reel which is a combination of multiple video clips."
    output_path = "final_reel.mp4"

    reel_generator = FinalReelGenerator()
    reel_generator.create_reel(video_clips, script, output_path)
