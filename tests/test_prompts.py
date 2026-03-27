import pytest

from video_summarizer.summarization import build_summary_prompt
from video_summarizer.transcription import build_transcription_prompt, normalize_language_choice


def test_normalize_language_choice():
    assert normalize_language_choice("Hebrew") == "he"
    assert normalize_language_choice("English") == "en"
    assert normalize_language_choice("fr") == "fr"


def test_build_transcription_prompt_mentions_language():
    prompt = build_transcription_prompt("Hebrew")
    assert "Hebrew" in prompt
    assert "study material" in prompt


def test_build_summary_prompt_base():
    prompt = build_summary_prompt("transcript", "Hebrew", "base")
    assert "Transcript:" in prompt
    assert "Hebrew" in prompt


def test_build_summary_prompt_agent_mentions_web_search():
    prompt = build_summary_prompt("transcript", "English", "agent")
    assert "web search" in prompt.lower()


def test_build_summary_prompt_rejects_unknown_mode():
    with pytest.raises(ValueError):
        build_summary_prompt("transcript", "Hebrew", "unknown")
