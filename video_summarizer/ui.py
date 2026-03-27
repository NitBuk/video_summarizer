from __future__ import annotations

from pathlib import Path

from .config import load_config
from .media import MediaProcessingError, extract_and_clean_audio
from .output import create_run_artifacts, save_summary_as_pdf, save_text
from .summarization import SUMMARY_MODE_LABELS, summarize_transcript
from .transcription import build_transcription_prompt, transcribe_audio


def _save_upload(uploaded_file, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def _get_openai_client(api_key: str | None):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def _reset_workflow_state() -> None:
    import streamlit as st

    for key in ("artifacts", "audio_chunks", "transcript", "summary"):
        st.session_state.pop(key, None)


def main() -> None:
    import streamlit as st

    config = load_config()
    st.set_page_config(page_title="Video Summarizer", layout="centered")
    st.title("Lecture Video Summarizer")
    st.caption("Manual, inspectable processing for lecture-style videos.")

    if not config.openai_api_key:
        st.warning("OPENAI_API_KEY is not set. Upload and audio extraction can still run locally.")

    uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_video is None:
        st.info("Upload a video to start the pipeline.")
        return

    if "current_upload_name" not in st.session_state or st.session_state.current_upload_name != uploaded_video.name:
        _reset_workflow_state()
        st.session_state.current_upload_name = uploaded_video.name

    artifacts = st.session_state.get("artifacts")
    if artifacts is None:
        artifacts = create_run_artifacts(config.output_dir, uploaded_video.name)
        st.session_state.artifacts = artifacts

    st.write(f"Run directory: `{artifacts.run_dir}`")
    st.write("Pipeline: video -> audio extraction -> transcription -> summary generation -> export/output")

    language = st.radio("Lecture language", ["Hebrew", "English"], horizontal=True)
    summary_mode = st.radio(
        "Summary mode",
        list(SUMMARY_MODE_LABELS.keys()),
        format_func=SUMMARY_MODE_LABELS.get,
        horizontal=True,
    )

    if st.button("Prepare audio chunks", use_container_width=True):
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
            st.success(f"Prepared {len(chunks)} cleaned audio chunk(s).")
        except MediaProcessingError as exc:
            st.error(f"Audio processing failed: {exc}")

    audio_chunks = st.session_state.get("audio_chunks", [])
    if audio_chunks:
        st.write(f"Cleaned audio chunks: {len(audio_chunks)}")

    if audio_chunks and st.button("Transcribe audio", use_container_width=True):
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

        if st.button("Generate summary", use_container_width=True):
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
                st.success("Summary generated.")

    summary = st.session_state.get("summary")
    if summary:
        st.text_area("Summary", summary, height=340)
        if st.button("Export summary as PDF", use_container_width=True):
            save_summary_as_pdf(
                summary,
                artifacts.summary_pdf_path,
                pdf_font_path=config.pdf_font_path,
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
