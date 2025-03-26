import os
import subprocess
from dotenv import load_dotenv
from modules.transcription import transcribe_audio

# Load the API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Path to the audio file you want to test
audio_chunk_path = "outputs/audio_chunk_000.wav"

# Processed (cleaned) audio file path
cleaned_audio_path = "outputs/audio_chunk_000_cleaned.wav"

# Step 1: Normalize volume and trim silence
subprocess.run([
    "ffmpeg", "-y", "-i", audio_chunk_path,
    "-af", "loudnorm,silenceremove=start_periods=1:start_threshold=-50dB",
    "-acodec", "pcm_s16le",
    "-ac", "1",
    "-ar", "16000",
    cleaned_audio_path
], check=True)

# Prompt for context
prompt = (
    "This is a lecture in Hebrew. Please transcribe the full content clearly."
)

# Language ("english" or "hebrew")
language = "hebrew"

# Transcribe and print result
transcript = transcribe_audio(api_key, cleaned_audio_path, prompt=prompt, language=language)
print("\n--- TRANSCRIPT ---\n")
print(transcript)