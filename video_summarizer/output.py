from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import wrap
from typing import Any


@dataclass(frozen=True)
class RunArtifacts:
    run_dir: Path
    input_dir: Path
    raw_audio_dir: Path
    cleaned_audio_dir: Path
    source_video_path: Path
    transcript_path: Path
    summary_markdown_path: Path
    summary_pdf_path: Path
    run_manifest_path: Path


def sanitize_filename(filename: str) -> str:
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-_.") or "upload"
    return f"{slug}{suffix}"


def build_run_directory_name(source_name: str, now: datetime | None = None) -> str:
    timestamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    return f"{sanitize_filename(source_name).rsplit('.', 1)[0]}-{timestamp}"


def create_run_artifacts(
    base_dir: Path,
    source_name: str,
    now: datetime | None = None,
) -> RunArtifacts:
    run_dir = base_dir / build_run_directory_name(source_name, now=now)
    input_dir = run_dir / "input"
    raw_audio_dir = run_dir / "audio" / "raw"
    cleaned_audio_dir = run_dir / "audio" / "cleaned"
    source_video_path = input_dir / sanitize_filename(source_name)
    transcript_path = run_dir / "transcript.txt"
    summary_markdown_path = run_dir / "summary.md"
    summary_pdf_path = run_dir / "summary.pdf"
    run_manifest_path = run_dir / "run_manifest.json"

    for directory in (input_dir, raw_audio_dir, cleaned_audio_dir):
        directory.mkdir(parents=True, exist_ok=True)

    return RunArtifacts(
        run_dir=run_dir,
        input_dir=input_dir,
        raw_audio_dir=raw_audio_dir,
        cleaned_audio_dir=cleaned_audio_dir,
        source_video_path=source_video_path,
        transcript_path=transcript_path,
        summary_markdown_path=summary_markdown_path,
        summary_pdf_path=summary_pdf_path,
        run_manifest_path=run_manifest_path,
    )


def save_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_summary_markdown(summary_text: str, *, title: str = "Lesson Summary") -> str:
    body = normalize_pdf_text(summary_text).strip()
    if body:
        return f"# {title}\n\n{body}\n"
    return f"# {title}\n"


def save_summary_as_markdown(
    summary_text: str,
    output_path: Path,
    *,
    title: str = "Lesson Summary",
) -> Path:
    return save_text(output_path, build_summary_markdown(summary_text, title=title))


def build_run_manifest(
    *,
    artifacts: RunArtifacts,
    source_name: str,
    status: str,
    language: str,
    summary_mode: str,
    openai_enabled: bool,
    transcription_model: str,
    summary_model: str,
    chunk_duration_seconds: int,
    audio_chunk_count: int | None = None,
    transcript_char_count: int | None = None,
    summary_char_count: int | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    generated_at = (now or datetime.now(timezone.utc)).isoformat()
    return {
        "schema_version": 1,
        "generated_at_utc": generated_at,
        "status": status,
        "source": {
            "name": source_name,
            "video_path": str(artifacts.source_video_path),
        },
        "runtime": {
            "openai_enabled": openai_enabled,
            "transcription_model": transcription_model,
            "summary_model": summary_model,
            "chunk_duration_seconds": chunk_duration_seconds,
        },
        "workflow": {
            "language": language,
            "summary_mode": summary_mode,
            "audio_chunk_count": audio_chunk_count,
            "transcript_char_count": transcript_char_count,
            "summary_char_count": summary_char_count,
        },
        "artifacts": {
            "run_dir": str(artifacts.run_dir),
            "input_dir": str(artifacts.input_dir),
            "raw_audio_dir": str(artifacts.raw_audio_dir),
            "cleaned_audio_dir": str(artifacts.cleaned_audio_dir),
            "transcript_txt": str(artifacts.transcript_path),
            "summary_md": str(artifacts.summary_markdown_path),
            "summary_pdf": str(artifacts.summary_pdf_path),
        },
    }


def save_run_manifest(path: Path, manifest: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def normalize_pdf_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _find_unicode_font(pdf_font_path: Path | None = None) -> Path | None:
    if pdf_font_path and pdf_font_path.exists():
        return pdf_font_path

    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
        Path("/Library/Fonts/DejaVu Sans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def save_summary_as_pdf(
    summary_text: str,
    output_path: Path,
    *,
    title: str = "Lesson Summary",
    pdf_font_path: Path | None = None,
) -> Path:
    from fpdf import FPDF

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    unicode_font = _find_unicode_font(pdf_font_path)
    if unicode_font is not None:
        pdf.add_font("UnicodeFont", "", str(unicode_font))
        pdf.set_font("UnicodeFont", size=12)
    else:
        pdf.set_font("Helvetica", size=12)

    pdf.multi_cell(0, 8, title)
    pdf.ln(2)

    text = normalize_pdf_text(summary_text)
    if unicode_font is None:
        text = text.encode("latin-1", "replace").decode("latin-1")

    for paragraph in text.split("\n"):
        if not paragraph.strip():
            pdf.ln(2)
            continue
        for line in wrap(paragraph, width=90) or [""]:
            pdf.multi_cell(0, 8, line)

    pdf.output(str(output_path))
    return output_path
