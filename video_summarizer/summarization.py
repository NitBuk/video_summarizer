from __future__ import annotations

SUMMARY_MODE_LABELS = {
    "base": "Base summarizer",
    "agent": "Agent summarizer",
}


def build_summary_prompt(transcript: str, language: str, mode: str) -> str:
    language_note = f"Keep the summary in {language}."
    base_prompt = (
        "You're an educational assistant tasked with summarizing recorded lectures. "
        "Generate a detailed, student-friendly summary that covers the main ideas, key points, "
        "important examples, and critical concepts."
    )

    if mode == "base":
        return f"{base_prompt} {language_note}\n\nTranscript:\n{transcript}"
    if mode == "agent":
        return (
            f"{base_prompt} {language_note} "
            "Use web search to clarify unclear or domain-specific terms before summarizing.\n\n"
            f"Transcript:\n{transcript}"
        )

    raise ValueError(f"Unsupported summary mode: {mode}")


def summarize_transcript(
    client,
    transcript: str,
    *,
    language: str,
    mode: str,
    model: str = "gpt-4o",
) -> str:
    prompt = build_summary_prompt(transcript, language, mode)
    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }

    if mode == "agent":
        kwargs["tools"] = [{"type": "web_search"}]
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content.strip()
