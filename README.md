# Video Summarizer

Video Summarizer is a Streamlit app for turning lecture-style videos into transcripts and study-ready summaries. The repo keeps the original manual workflow on purpose: you can inspect each step, rerun any stage, and see exactly where generated artifacts are written.

This repo is local-first. There is no production deployment wired into the codebase today.

## What it does

- Upload a video in `mp4`, `mov`, `avi`, or `mkv` format.
- Extract audio with `ffmpeg`, then normalize and trim each chunk.
- Transcribe each cleaned audio chunk with the OpenAI transcription API.
- Generate either a base summary or a web-search-aware summary.
- Export the summary as text in the UI and as a PDF artifact on disk.

## Pipeline

`video -> audio extraction -> transcription -> summary generation -> export/output`

The app stores each run in its own folder under `outputs/`, so the source video, audio chunks, transcript, and PDF are kept together for debugging and review.

## What is local vs API-backed

Local only:

- Video upload and artifact management
- Audio chunking and cleanup with `ffmpeg`
- Transcript and PDF file writing
- Prompt construction and run-directory layout

API-backed:

- Audio transcription via OpenAI
- Summary generation via OpenAI
- Optional agent-style summary mode that can use web search if the model/account supports it

## Project structure

```text
video_summarizer/
├── app.py
├── video_summarizer/
│   ├── config.py
│   ├── media.py
│   ├── output.py
│   ├── summarization.py
│   ├── transcription.py
│   └── ui.py
├── tests/
├── .env.example
├── pyproject.toml
└── outputs/            # generated at runtime
```

## Quick start

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install the project and dev tools.

```bash
pip install -e .[dev]
```

3. Create your local environment file.

```bash
cp .env.example .env
```

4. Set `OPENAI_API_KEY` in `.env`.

5. Install `ffmpeg` and make sure it is on your `PATH`.

6. Start the app.

```bash
streamlit run app.py
```

For the fastest demo, upload a short clip so the audio chunking and API calls finish quickly.

## Developer workflow

- Run tests: `pytest`
- Lint: `ruff check .`
- Format check: `ruff format --check .`
- App entrypoint: `app.py`
- UI logic: `video_summarizer/ui.py`
- Audio processing: `video_summarizer/media.py`
- Transcription API wrapper: `video_summarizer/transcription.py`
- Summary generation: `video_summarizer/summarization.py`
- Artifact writing and PDF export: `video_summarizer/output.py`

## Output layout

Each upload gets its own run folder, for example:

```text
outputs/
└── lecture-clip-20260327-100506/
    ├── input/
    │   └── lecture-clip.mp4
    ├── audio/
    │   ├── raw/
    │   └── cleaned/
    ├── transcript.txt
    └── summary.pdf
```

## Limitations

- This repo still depends on OpenAI for transcription and summarization.
- `ffmpeg` must be installed locally for audio extraction to work.
- PDF export is best effort. If a Unicode font is available locally or configured through `PDF_FONT_PATH`, the PDF can render more languages. Otherwise it falls back to a basic core font and may replace unsupported characters.
- The app is intentionally manual rather than fully automated, so each stage remains visible and debuggable.

## What this demonstrates

- A clean Streamlit app with a clearly separated processing pipeline.
- Practical Python packaging and environment handling with `pyproject.toml`.
- Defensive artifact management instead of dumping everything into one folder.
- Honest documentation about what is local, what uses APIs, and where the limitations are.
- Basic tests for deterministic logic that do not need network access.

## Recent improvements

- Replaced the old flat `modules/` layout with a real package.
- Removed tracked IDE files and added better repo hygiene.
- Switched from key-in-code setup to `.env.example` and environment loading.
- Added reproducible install instructions, lint/test commands, and CI.
- Made PDF export configurable instead of depending on a hard-coded local font file.
