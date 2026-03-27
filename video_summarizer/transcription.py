from __future__ import annotations

from pathlib import Path

LANGUAGE_CODES = {
    "hebrew": "he",
    "english": "en",
}


def normalize_language_choice(language: str | None) -> str | None:
    if language is None:
        return None

    normalized = language.strip().lower()
    return LANGUAGE_CODES.get(normalized, normalized[:2] if len(normalized) >= 2 else None)


def build_transcription_prompt(language: str) -> str:
    return (
        f"The following audio is a recorded class lecture in {language}. "
        "Please transcribe it completely and accurately, capturing explanations, technical details, "
        "examples, and key concepts. The transcript will be used as study material."
    )


def transcribe_audio(
    client,
    audio_file_path: Path,
    *,
    prompt: str | None = None,
    language: str | None = None,
    model: str = "gpt-4o-transcribe",
) -> str:
    language_code = normalize_language_choice(language)
    with audio_file_path.open("rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="text",
            prompt=prompt,
            language=language_code,
        )

    return transcription.strip() if isinstance(transcription, str) else str(transcription).strip()
