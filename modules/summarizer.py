from openai import OpenAI

def base_summarizer(api_key, transcript):
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You're an educational assistant tasked with summarizing recorded lectures. 
    Generate a student-friendly summary from the transcript below.
    Keep the summary detailed and thorough, covering all main ideas, key points, important examples, and critical concepts.
    Don't change the language or tone of the original transcript. i.e. if it is in Hebrew, keep it in Hebrew.
    Transcript:
    {transcript}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


def agent_summarizer(api_key, transcript):
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You're an educational assistant tasked with summarizing recorded lectures.
    Generate a summary from the transcript below.
    Keep the summary detailed and thorough, covering all main ideas, key points, important examples, and critical concepts.
    Don't change the language or tone of the original transcript. i.e. if it is in Hebrew, keep it in Hebrew.
    Use web search to clarify any unclear or complex concepts before summarizing.

    Transcript:
    {transcript}
    """

    tools = [{"type": "web_search"}]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice="auto"
    )

    return response.choices[0].message.content