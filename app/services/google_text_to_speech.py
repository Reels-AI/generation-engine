import os
from google.cloud import texttospeech, speech

# Set the environment variable for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "newsappbuddy-c619b537c3af.json"


class GoogleCloudAudioProcessor:
    def __init__(self, tts_language_code="en-US", tts_voice_name="en-US-Neural2-J", tts_speaking_rate=1.2):
        """
        Initialize the GoogleCloudAudioProcessor.

        Args:
            tts_language_code (str): Language code for the text-to-speech voice.
            tts_voice_name (str): Voice name for text-to-speech.
            tts_speaking_rate (float): Speaking rate for text-to-speech.
        """
        self.tts_language_code = tts_language_code
        self.tts_voice_name = tts_voice_name
        self.tts_speaking_rate = tts_speaking_rate

    def generate_google_tts_audio(self, text):
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=self.tts_language_code,
            name=self.tts_voice_name,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=self.tts_speaking_rate,
        )

        request = texttospeech.SynthesizeSpeechRequest(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        try:
            response = client.synthesize_speech(request=request)
            print("Generated Audio for Podcast Script")
            return response.audio_content
        except Exception as error:
            print(f"Error Generating Audio for Podcast Script: {error}")
            return False

    def transcribe_audio_with_timestamps(self, audio_content, original_text):
        client = speech.SpeechClient()

        audio = speech.RecognitionAudio(content=audio_content)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=44100,
            language_code="en-US",
            enable_word_time_offsets=True
        )

        response = client.recognize(config=config, audio=audio)

        word_timings = []
        for result in response.results:
            alternative = result.alternatives[0]
            for word_info in alternative.words:
                word = word_info.word
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()
                word_timings.append((word, start_time, end_time))

        return self.correct_transcription(word_timings, original_text)

    def correct_transcription(self, transcribed_data, correct_text):
        correct_words = correct_text.split()

        corrected_transcription = []
        correct_index = 0
        current_start_time = None
        last_word = None

        for transcribed_word, t_start_time, t_end_time in transcribed_data:
            if correct_index >= len(correct_words):
                break

            correct_word = correct_words[correct_index]

            if current_start_time is None:
                current_start_time = t_start_time

            if transcribed_word != correct_word:
                if last_word == correct_word:
                    corrected_transcription[-1] = (correct_word,
                                                   corrected_transcription[-1][1], t_end_time)
                else:
                    corrected_transcription.append(
                        (correct_word, current_start_time, t_end_time))
                correct_index += 1
                last_word = correct_word
                current_start_time = None
            else:
                end_time = t_end_time
                if correct_index == len(correct_words) - 1 or transcribed_word == correct_word:
                    if last_word == correct_word:
                        corrected_transcription[-1] = (correct_word,
                                                       corrected_transcription[-1][1], end_time)
                    else:
                        corrected_transcription.append(
                            (correct_word, current_start_time, end_time))
                    correct_index += 1
                    last_word = correct_word
                    current_start_time = None

        while correct_index < len(correct_words):
            correct_word = correct_words[correct_index]
            if corrected_transcription and corrected_transcription[-1][0] == correct_word:
                corrected_transcription[-1] = (correct_word,
                                               corrected_transcription[-1][1], end_time)
            else:
                corrected_transcription.append(
                    (correct_word, current_start_time, end_time))
            correct_index += 1

        return corrected_transcription


# Example usage
# if __name__ == "__main__":
#     processor = GoogleCloudAudioProcessor()
#     text = "This is a test."
#     audio_content = processor.generate_google_tts_audio(text)
#     if audio_content:
#         original_text = "This is a test."
#         transcribed = processor.transcribe_audio_with_timestamps(audio_content, original_text)
#         print(transcribed)
