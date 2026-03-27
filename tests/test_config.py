from video_summarizer.config import load_config


def test_load_config_uses_env_values(tmp_path):
    config = load_config(
        {
            "OPENAI_API_KEY": "secret",
            "OUTPUT_DIR": str(tmp_path / "artifacts"),
            "OPENAI_TRANSCRIPTION_MODEL": "transcribe-model",
            "OPENAI_SUMMARY_MODEL": "summary-model",
            "CHUNK_DURATION_SECONDS": "120",
            "PDF_FONT_PATH": "",
        }
    )

    assert config.openai_api_key == "secret"
    assert config.output_dir == tmp_path / "artifacts"
    assert config.transcription_model == "transcribe-model"
    assert config.summary_model == "summary-model"
    assert config.chunk_duration_seconds == 120
    assert config.pdf_font_path is None
