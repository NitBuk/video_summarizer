from openai import OpenAI

LANGUAGE_CODES = {
    "hebrew": "he",
    "english": "en"
}

def transcribe_audio(api_key, audio_file_path, prompt=None, language=None):
    client = OpenAI(api_key=api_key)

    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            response_format="text",
            prompt=prompt,
            language=LANGUAGE_CODES.get(language.lower()) if language else None
        )

    return transcription