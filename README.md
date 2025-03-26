# 📚 Lesson Summarizer (v0.0.1)

Welcome to **Lesson Summarizer v0.0.1**, a Streamlit-based web application that enables students, educators, and content creators to upload video lessons (in Hebrew or English), transcribe the spoken content, and generate a structured summary suitable for study purposes.

This version is an MVP (Minimum Viable Product) focused on manually controlled processing steps, allowing clear visibility and control over each part of the workflow.

---

## 🎯 Features

- **Video Upload**: Supports `.mp4`, `.mov`, and `.avi` formats.
- **Audio Extraction and Cleaning**:
  - Extracts mono-channel 16-bit WAV audio from uploaded video.
  - Applies silence trimming and audio normalization for improved transcription quality.
- **Manual Transcription**:
  - Transcribes segmented audio chunks using OpenAI's GPT-4o Transcribe model.
  - User chooses between Hebrew and English for language accuracy.
  - Prompts can be tailored to ensure educational transcription quality.
- **Transcript Export**:
  - Complete transcript is displayed and can be downloaded as a `.txt` file.
- **Manual Summarization**:
  - Choose between two summarization modes:
    - **Base Summarizer** (faster, cheaper)
    - **Agent Summarizer** (enhanced with web-search awareness)
- **Summary Export**:
  - Displays full summary.
  - Downloadable as a PDF file.

---

## 🧪 Version Notes: v0.0.1 (Manual Control Focus)

In this version, the entire process is **user-controlled step-by-step**:

1. **Video Upload**: User manually uploads the file.
2. **Extract & Clean Audio**: Triggered manually by the user.
3. **Transcription**: Executed only when the user clicks the "Transcribe Audio" button.
4. **Transcript Review & Download**: Displayed immediately and saved as a `.txt` file.
5. **Summary Generation**: Controlled by selecting the method and clicking "Generate Summary".
6. **Summary Download**: Available once the summary is ready.

This manual architecture is intentional for early testing and transparency. It also aids debugging and experimentation with model behaviors.

---

## ⚙️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io)
- **Audio Processing**: [ffmpeg](https://ffmpeg.org)
- **Transcription & Summarization**: [OpenAI GPT-4o](https://platform.openai.com)
- **PDF Generation**: `reportlab`
- **Environment Configuration**: `python-dotenv`

---

## 🛠 Setup Instructions

1. **Clone the repo**:
```bash
https://github.com/your-username/video-summarizer.git
cd video-summarizer
```

2. **Install dependencies**:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3. **Add your OpenAI API key**:
Create a `.env` file with:
```
OPENAI_API_KEY=your-key-here
```

4. **Install ffmpeg**:
Ensure `ffmpeg` is installed and accessible via CLI.

5. **Run the app**:
```bash
streamlit run app.py --server.maxUploadSize 1000
```

---

## 📁 Project Structure
```
video_summarizer/
├── app.py                     # Main Streamlit app
├── modules/
│   ├── audio_utils.py        # Audio extraction and cleaning functions
│   ├── transcription.py      # Transcription logic with OpenAI API
│   ├── summarizer.py         # Base and agent summarizers
│   └── pdf_generator.py      # Summary PDF export utility
├── outputs/                  # Temporary storage for audio, transcript, and PDFs
├── .env                      # API key config
└── requirements.txt
```

---

## 🚧 Coming Soon (v0.1.0+)

- Auto-processing pipeline (no manual clicks required)
- Multi-language support detection and correction
- Support for uploading audio-only files
- Enhanced UI feedback and processing status
- Cloud deployment with session management

---

## 🙋‍♂️ Contributing
This project is in its early stages. Feel free to open issues or suggest improvements!

---

## 📄 License
MIT License

---

Created with ❤️ by Nitzan Buk. Feedback and collaboration ideas are welcome!

