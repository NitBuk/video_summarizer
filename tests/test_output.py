from datetime import datetime, timezone

from video_summarizer.output import (
    build_run_directory_name,
    create_run_artifacts,
    normalize_pdf_text,
    sanitize_filename,
)


def test_sanitize_filename_keeps_extension():
    assert sanitize_filename("My Lecture (Final).mp4") == "My-Lecture-Final.mp4"


def test_build_run_directory_name_is_timestamped():
    fixed_now = datetime(2026, 3, 27, 10, 5, 6, tzinfo=timezone.utc)
    assert build_run_directory_name("Lecture 01.mp4", now=fixed_now) == "Lecture-01-20260327-100506"


def test_create_run_artifacts(tmp_path):
    fixed_now = datetime(2026, 3, 27, 10, 5, 6, tzinfo=timezone.utc)
    artifacts = create_run_artifacts(tmp_path, "Lecture 01.mp4", now=fixed_now)

    assert artifacts.run_dir == tmp_path / "Lecture-01-20260327-100506"
    assert artifacts.source_video_path.name == "Lecture-01.mp4"
    assert artifacts.transcript_path.name == "transcript.txt"
    assert artifacts.summary_pdf_path.name == "summary.pdf"
    assert artifacts.raw_audio_dir.exists()
    assert artifacts.cleaned_audio_dir.exists()


def test_normalize_pdf_text():
    assert normalize_pdf_text("line1\r\nline2\rline3") == "line1\nline2\nline3"
