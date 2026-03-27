from __future__ import annotations

from pathlib import Path
import subprocess


class MediaProcessingError(RuntimeError):
    """Raised when ffmpeg-based processing fails."""


def build_chunk_template(output_dir: Path) -> Path:
    return output_dir / "audio_chunk_%03d.wav"


def build_cleaned_chunk_path(raw_chunk_path: Path, cleaned_dir: Path) -> Path:
    return cleaned_dir / f"cleaned_{raw_chunk_path.name}"


def _run_ffmpeg(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        message = stderr or "ffmpeg exited with a non-zero status."
        raise MediaProcessingError(message)


def extract_audio_chunks(
    video_path: Path,
    raw_audio_dir: Path,
    chunk_duration_seconds: int = 1490,
) -> list[Path]:
    raw_audio_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "segment",
        "-segment_time",
        str(chunk_duration_seconds),
        str(build_chunk_template(raw_audio_dir)),
    ]
    _run_ffmpeg(command)
    return sorted(raw_audio_dir.glob("audio_chunk_*.wav"))


def clean_audio(input_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-af",
        "loudnorm,silenceremove=start_periods=1:start_threshold=-50dB",
        "-acodec",
        "pcm_s16le",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_path),
    ]
    _run_ffmpeg(command)
    return output_path


def extract_and_clean_audio(
    video_path: Path,
    raw_audio_dir: Path,
    cleaned_audio_dir: Path,
    chunk_duration_seconds: int = 1490,
) -> list[Path]:
    raw_chunks = extract_audio_chunks(video_path, raw_audio_dir, chunk_duration_seconds)
    cleaned_chunks = []
    for raw_path in raw_chunks:
        cleaned_path = build_cleaned_chunk_path(raw_path, cleaned_audio_dir)
        cleaned_chunks.append(clean_audio(raw_path, cleaned_path))
    return cleaned_chunks
