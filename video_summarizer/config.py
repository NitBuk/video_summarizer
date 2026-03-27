from __future__ import annotations

import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str | None
    output_dir: Path
    transcription_model: str
    summary_model: str
    chunk_duration_seconds: int
    pdf_font_path: Path | None


@dataclass(frozen=True)
class PreflightReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ffmpeg_path: str | None = None


def _parse_optional_path(raw_value: str | None) -> Path | None:
    if raw_value is None or not raw_value.strip():
        return None
    return Path(raw_value).expanduser()


def _resolve_relative_path(path: Path, repo_root: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def load_config(environ: Mapping[str, str] | None = None) -> AppConfig:
    """Load environment-backed settings for the app."""

    _load_dotenv()
    env = os.environ if environ is None else environ
    repo_root = Path(__file__).resolve().parent.parent

    output_dir = _resolve_relative_path(
        Path(env.get("OUTPUT_DIR", "outputs")).expanduser(),
        repo_root,
    )
    chunk_duration = int(env.get("CHUNK_DURATION_SECONDS", "1490"))

    return AppConfig(
        openai_api_key=env.get("OPENAI_API_KEY") or None,
        output_dir=output_dir,
        transcription_model=env.get("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-transcribe"),
        summary_model=env.get("OPENAI_SUMMARY_MODEL", "gpt-4o"),
        chunk_duration_seconds=chunk_duration,
        pdf_font_path=(
            _resolve_relative_path(font_path, repo_root)
            if (font_path := _parse_optional_path(env.get("PDF_FONT_PATH"))) is not None
            else None
        ),
    )


def validate_runtime(config: AppConfig) -> PreflightReport:
    """Check the local runtime for the most important pipeline dependencies."""

    errors: list[str] = []
    warnings: list[str] = []
    ffmpeg_path = shutil.which("ffmpeg")

    if ffmpeg_path is None:
        errors.append(
            "ffmpeg was not found on PATH. Audio extraction and cleaning will not work "
            "until ffmpeg is installed."
        )

    if config.chunk_duration_seconds <= 0:
        errors.append("CHUNK_DURATION_SECONDS must be a positive integer.")

    if not config.openai_api_key:
        warnings.append(
            "OPENAI_API_KEY is not set. Uploading and local preprocessing still work, "
            "but transcription and summary generation are disabled."
        )

    return PreflightReport(errors=errors, warnings=warnings, ffmpeg_path=ffmpeg_path)
