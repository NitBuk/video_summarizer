from datetime import datetime, timezone

from video_summarizer.output import (
    build_run_directory_name,
    build_run_manifest,
    build_summary_markdown,
    create_run_artifacts,
    normalize_pdf_text,
    sanitize_filename,
    save_run_manifest,
    save_summary_as_markdown,
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
    assert artifacts.summary_markdown_path.name == "summary.md"
    assert artifacts.summary_pdf_path.name == "summary.pdf"
    assert artifacts.run_manifest_path.name == "run_manifest.json"
    assert artifacts.raw_audio_dir.exists()
    assert artifacts.cleaned_audio_dir.exists()


def test_normalize_pdf_text():
    assert normalize_pdf_text("line1\r\nline2\rline3") == "line1\nline2\nline3"


def test_build_summary_markdown():
    markdown = build_summary_markdown("First line\nSecond line")
    assert markdown.startswith("# Lesson Summary")
    assert "First line" in markdown
    assert markdown.endswith("\n")


def test_build_run_manifest_and_save(tmp_path):
    fixed_now = datetime(2026, 3, 27, 10, 5, 6, tzinfo=timezone.utc)
    artifacts = create_run_artifacts(tmp_path, "Lecture 01.mp4", now=fixed_now)
    manifest = build_run_manifest(
        artifacts=artifacts,
        source_name="Lecture 01.mp4",
        status="summary_generated",
        language="Hebrew",
        summary_mode="base",
        openai_enabled=True,
        transcription_model="transcribe-model",
        summary_model="summary-model",
        chunk_duration_seconds=120,
        audio_chunk_count=3,
        transcript_char_count=42,
        summary_char_count=99,
        now=fixed_now,
    )

    assert manifest["status"] == "summary_generated"
    assert manifest["workflow"]["audio_chunk_count"] == 3
    assert manifest["artifacts"]["summary_md"].endswith("summary.md")

    saved = save_run_manifest(artifacts.run_manifest_path, manifest)
    assert saved.read_text(encoding="utf-8").startswith("{\n")


def test_save_summary_as_markdown(tmp_path):
    path = tmp_path / "summary.md"
    saved = save_summary_as_markdown("hello", path)

    assert saved == path
    assert path.read_text(encoding="utf-8") == "# Lesson Summary\n\nhello\n"
