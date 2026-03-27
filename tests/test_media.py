from video_summarizer.media import build_chunk_template, build_cleaned_chunk_path


def test_build_chunk_template(tmp_path):
    assert build_chunk_template(tmp_path) == tmp_path / "audio_chunk_%03d.wav"


def test_build_cleaned_chunk_path(tmp_path):
    raw_chunk = tmp_path / "audio_chunk_001.wav"
    cleaned_dir = tmp_path / "cleaned"

    assert build_cleaned_chunk_path(raw_chunk, cleaned_dir) == cleaned_dir / "cleaned_audio_chunk_001.wav"
