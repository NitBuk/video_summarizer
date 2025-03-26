import streamlit as st
import os
from dotenv import load_dotenv
from modules.audio_utils import extract_and_clean_audio
from modules.transcription import transcribe_audio
from modules.summarizer import base_summarizer, agent_summarizer
from modules.pdf_generator import save_summary_as_pdf

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="🎓 Lesson Summarizer", layout="centered")
st.title("🎓 Hebrew/English Video Summarizer")

uploaded_video = st.file_uploader("📹 Upload a video file", type=["mp4", "mov", "avi"])

if uploaded_video:
    video_path = os.path.join(OUTPUT_DIR, "video.mp4")
    pdf_path = os.path.join(OUTPUT_DIR, "summary.pdf")

    if st.button("🔊 Extract & Clean Audio"):
        with open(video_path, "wb") as f:
            f.write(uploaded_video.read())

        audio_files = extract_and_clean_audio(video_path, OUTPUT_DIR)
        st.session_state.audio_files = audio_files
        st.success("✅ Audio extraction and cleaning complete.")

    audio_files = st.session_state.get("audio_files", [])

    language = st.radio("🌐 Select lecture language:", ["Hebrew", "English"])

    if st.button("📝 Transcribe Audio"):
        transcript = ""
        prompt = (
            f"The following audio is a recorded class lecture in {language}. Please transcribe it completely and accurately, "
            "capturing all explanations, technical details, examples, and key concepts. "
            "The transcript will be used as detailed study material by students."
        )

        for file in audio_files:
            st.info(f"Transcribing {os.path.basename(file)}...")
            transcript += transcribe_audio(api_key, file, prompt=prompt, language=language.lower()) + "\n\n"

        # Save transcript to file
        transcript_path = os.path.join(OUTPUT_DIR, "transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        # Store transcript in session state
        st.session_state.transcript = transcript

        # Clean up other files in outputs except the transcript
        for filename in os.listdir(OUTPUT_DIR):
            file_path = os.path.join(OUTPUT_DIR, filename)
            if file_path != transcript_path and os.path.isfile(file_path):
                os.remove(file_path)

        st.session_state.transcript_path = transcript_path

        st.text_area("📜 Transcript", transcript, height=300)

        with open(st.session_state.transcript_path, "rb") as f:
            st.download_button(
                label="📄 Download Transcript TXT",
                data=f,
                file_name="transcript.txt",
                mime="text/plain"
            )

if "transcript" in st.session_state:
    summary_method = st.radio(
        "🔧 Choose summarization method:",
        ["Base Summarizer (Fast, cheaper)", "Agent Summarizer (Higher accuracy, uses web search)"]
    )

    if st.button("📚 Generate Summary"):
        if summary_method == "Base Summarizer (Fast, cheaper)":
            prompt_summary = (
                "You're an educational assistant tasked with summarizing recorded lectures. "
                "Provide a detailed and thorough summary that clearly explains the main ideas, key points, "
                "important examples, and critical concepts covered in the lecture transcript. "
                "Ensure the summary is comprehensive enough to serve as detailed study notes for students."
            )
            summary = base_summarizer(api_key, st.session_state.transcript + "\n\n" + prompt_summary)
        else:
            prompt_summary = (
                "You're an educational assistant tasked with summarizing recorded lectures. "
                "Use web search to clarify complex or unclear terms first, then produce a comprehensive and detailed summary. "
                "Your summary should include key points, concepts, thorough explanations, and notable examples, ensuring it’s "
                "a useful and informative study resource for students."
            )
            summary = agent_summarizer(api_key, st.session_state.transcript + "\n\n" + prompt_summary)

        st.session_state.summary = summary
        st.text_area("📄 Summary", summary, height=500)

    if 'summary' in st.session_state:
        if st.button("📥 Generate PDF"):
            save_summary_as_pdf(st.session_state.summary, pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📩 Download Summary PDF",
                    data=f,
                    file_name="lesson_summary.pdf",
                    mime="application/pdf"
                )
            st.success("✅ PDF ready for download.")
else:
    st.warning("Please upload a video file.")