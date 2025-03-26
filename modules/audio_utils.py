import subprocess
import os
import glob

def extract_audio(video_path, output_dir, chunk_duration=1490):
    os.makedirs(output_dir, exist_ok=True)
    output_template = f"{output_dir}/audio_chunk_%03d.wav"

    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-acodec", "pcm_s16le",
        "-ac", "1",
        "-ar", "16000",
        "-f", "segment",
        "-segment_time", str(chunk_duration),
        output_template
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during audio extraction: {e}")
        return []

    return sorted(glob.glob(os.path.join(output_dir, "audio_chunk_*.wav")))

def clean_audio(input_path, output_path):
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-af", "loudnorm,silenceremove=start_periods=1:start_threshold=-50dB",
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",
            output_path
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error cleaning audio: {e}")
        return False

def extract_and_clean_audio(video_path, output_dir, chunk_duration=1490):
    raw_chunks = extract_audio(video_path, output_dir, chunk_duration)
    cleaned_chunks = []

    for raw_path in raw_chunks:
        base_name = os.path.basename(raw_path)
        cleaned_path = os.path.join(output_dir, f"cleaned_{base_name}")
        if clean_audio(raw_path, cleaned_path):
            cleaned_chunks.append(cleaned_path)
        else:
            print(f"Failed to clean {raw_path}, skipping.")

    return cleaned_chunks