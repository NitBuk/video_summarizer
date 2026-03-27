from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import os


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
