from __future__ import annotations

import json
from pathlib import Path

from .config import load_config, validate_runtime
from .media import MediaProcessingError, extract_and_clean_audio
from .output import (
    build_run_manifest,
    create_run_artifacts,
    save_run_manifest,
    save_summary_as_markdown,
    save_summary_as_pdf,
    save_text,
)
from .summarization import SUMMARY_MODE_LABELS, summarize_transcript
from .transcription import build_transcription_prompt, transcribe_audio


def _build_upload_token(uploaded_file) -> tuple[object, str, object]:
    return (
        getattr(uploaded_file, "file_id", None),
        uploaded_file.name,
        getattr(uploaded_file, "size", None),
    )


def _save_upload(uploaded_file, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def _get_openai_client(api_key: str | None):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def _reset_workflow_state() -> None:
    import streamlit as st

    for key in ("artifacts", "audio_chunks", "transcript", "summary", "run_manifest"):
        st.session_state.pop(key, None)


def _save_run_manifest(
    *,
    artifacts,
    config,
    source_name: str,
    stage: str,
    language: str,
    summary_mode: str,
    audio_chunk_count: int | None = None,
    transcript: str | None = None,
    summary: str | None = None,
) -> dict[str, object]:
    import streamlit as st

    manifest = build_run_manifest(
        artifacts=artifacts,
        source_name=source_name,
        status=stage,
        language=language,
        summary_mode=summary_mode,
        openai_enabled=bool(config.openai_api_key),
        transcription_model=config.transcription_model,
        summary_model=config.summary_model,
        chunk_duration_seconds=config.chunk_duration_seconds,
        audio_chunk_count=audio_chunk_count,
        transcript_char_count=len(transcript) if transcript is not None else None,
        summary_char_count=len(summary) if summary is not None else None,
    )
    save_run_manifest(artifacts.run_manifest_path, manifest)
    st.session_state.run_manifest = manifest
    return manifest


def main() -> None:
    import streamlit as st

    config = load_config()
    preflight = validate_runtime(config)
    st.set_page_config(page_title="Video Summarizer", layout="centered")
    st.title("Lecture Video Summarizer")
    st.caption("Manual, inspectable processing for lecture-style videos.")

    if preflight.ffmpeg_path:
        st.caption(f"ffmpeg detected at `{preflight.ffmpeg_path}`")
    else:
        st.error(
            "ffmpeg was not found on PATH. Audio extraction will not work until it is installed."
        )

    for warning in preflight.warnings:
        st.warning(warning)

    uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_video is None:
        if "current_upload_token" in st.session_state:
            _reset_workflow_state()
            st.session_state.pop("current_upload_token", None)
        st.info("Upload a video to start the pipeline.")
        return

    upload_token = _build_upload_token(uploaded_video)
    if (
        "current_upload_token" not in st.session_state
        or st.session_state.current_upload_token != upload_token
    ):
        _reset_workflow_state()
        st.session_state.current_upload_token = upload_token

    language = st.radio("Lecture language", ["Hebrew", "English"], horizontal=True)
    summary_mode = st.radio(
        "Summary mode",
        list(SUMMARY_MODE_LABELS.keys()),
        format_func=SUMMARY_MODE_LABELS.get,
        horizontal=True,
    )

    artifacts = st.session_state.get("artifacts")
    if artifacts is None:
        artifacts = create_run_artifacts(config.output_dir, uploaded_video.name)
        st.session_state.artifacts = artifacts
        _save_run_manifest(
            artifacts=artifacts,
            config=config,
            source_name=uploaded_video.name,
            stage="initialized",
            language=language,
            summary_mode=summary_mode,
        )

    st.write(f"Run directory: `{artifacts.run_dir}`")
    st.write(
        "Pipeline: video -> audio extraction -> transcription -> "
        "summary generation -> export/output"
    )

    prepare_disabled = bool(preflight.errors)
    if st.button("Prepare audio chunks", use_container_width=True, disabled=prepare_disabled):
        try:
            _save_upload(uploaded_video, artifacts.source_video_path)
            with st.spinner("Extracting and cleaning audio..."):
                chunks = extract_and_clean_audio(
                    artifacts.source_video_path,
                    artifacts.raw_audio_dir,
                    artifacts.cleaned_audio_dir,
                    chunk_duration_seconds=config.chunk_duration_seconds,
                )
            st.session_state.audio_chunks = chunks
            _save_run_manifest(
                artifacts=artifacts,
                config=config,
                source_name=uploaded_video.name,
                stage="audio_prepared",
                language=language,
                summary_mode=summary_mode,
                audio_chunk_count=len(chunks),
            )
            st.success(f"Prepared {len(chunks)} cleaned audio chunk(s).")
        except MediaProcessingError as exc:
            st.error(f"Audio processing failed: {exc}")

    audio_chunks = st.session_state.get("audio_chunks", [])
    if audio_chunks:
        st.write(f"Cleaned audio chunks: {len(audio_chunks)}")

    transcribe_disabled = not config.openai_api_key or bool(preflight.errors)
    if audio_chunks and st.button(
        "Transcribe audio",
        use_container_width=True,
        disabled=transcribe_disabled,
    ):
        if not config.openai_api_key:
            st.error("Set OPENAI_API_KEY before transcribing.")
        else:
            client = _get_openai_client(config.openai_api_key)
            prompt = build_transcription_prompt(language)
            parts: list[str] = []
            with st.spinner("Transcribing audio chunks..."):
                for index, chunk_path in enumerate(audio_chunks, start=1):
                    st.info(f"Transcribing chunk {index}/{len(audio_chunks)}: {chunk_path.name}")
                    parts.append(
                        transcribe_audio(
                            client,
                            Path(chunk_path),
                            prompt=prompt,
                            language=language,
                            model=config.transcription_model,
                        )
                    )
            transcript = "\n\n".join(part for part in parts if part.strip()).strip()
            save_text(artifacts.transcript_path, transcript)
            st.session_state.transcript = transcript
            _save_run_manifest(
                artifacts=artifacts,
                config=config,
                source_name=uploaded_video.name,
                stage="transcript_saved",
                language=language,
                summary_mode=summary_mode,
                audio_chunk_count=len(audio_chunks),
                transcript=transcript,
            )
            st.success("Transcript saved.")

    transcript = st.session_state.get("transcript")
    if transcript:
        st.text_area("Transcript", transcript, height=300)
        st.download_button(
            "Download transcript (.txt)",
            data=transcript.encode("utf-8"),
            file_name="transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )

        summarize_disabled = not config.openai_api_key or bool(preflight.errors)
        if st.button("Generate summary", use_container_width=True, disabled=summarize_disabled):
            if not config.openai_api_key:
                st.error("Set OPENAI_API_KEY before generating a summary.")
            else:
                client = _get_openai_client(config.openai_api_key)
                with st.spinner("Generating summary..."):
                    summary = summarize_transcript(
                        client,
                        transcript,
                        language=language,
                        mode=summary_mode,
                        model=config.summary_model,
                    )
                st.session_state.summary = summary
                save_summary_as_markdown(summary, artifacts.summary_markdown_path)
                st.success("Summary generated.")
                _save_run_manifest(
                    artifacts=artifacts,
                    config=config,
                    source_name=uploaded_video.name,
                    stage="summary_generated",
                    language=language,
                    summary_mode=summary_mode,
                    audio_chunk_count=len(audio_chunks),
                    transcript=transcript,
                    summary=summary,
                )

    summary = st.session_state.get("summary")
    if summary:
        st.text_area("Summary", summary, height=340)
        summary_markdown = artifacts.summary_markdown_path.read_text(encoding="utf-8")
        st.download_button(
            "Download summary (.md)",
            data=summary_markdown.encode("utf-8"),
            file_name="summary.md",
            mime="text/markdown",
            use_container_width=True,
        )
        if st.button("Export summary as PDF", use_container_width=True):
            save_summary_as_pdf(
                summary,
                artifacts.summary_pdf_path,
                pdf_font_path=config.pdf_font_path,
            )
            _save_run_manifest(
                artifacts=artifacts,
                config=config,
                source_name=uploaded_video.name,
                stage="summary_exported",
                language=language,
                summary_mode=summary_mode,
                audio_chunk_count=len(audio_chunks),
                transcript=transcript,
                summary=summary,
            )
            st.success("PDF exported.")

    if summary and artifacts.summary_pdf_path.exists():
        st.download_button(
            "Download summary PDF",
            data=artifacts.summary_pdf_path.read_bytes(),
            file_name="summary.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    if st.session_state.get("run_manifest"):
        manifest_json = json.dumps(st.session_state.run_manifest, indent=2, sort_keys=True)
        st.download_button(
            "Download run manifest (.json)",
            data=manifest_json.encode("utf-8"),
            file_name="run_manifest.json",
            mime="application/json",
            use_container_width=True,
        )
