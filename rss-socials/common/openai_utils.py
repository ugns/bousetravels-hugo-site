import os
import grapheme
from openai import OpenAI

POST_INSTRUCTIONS_TEMPLATE = """
Generate a {platform} post for my latest blog post.

The post must:
- Be under 300 graphemes
- Contain no more than three hashtags
- Entice the audience to click on the link without revealing all content

Use an engaging, appropriate tone for {platform}.

If the linked content is inappropriate, offensive, broken, or otherwise unsuitable for public sharing,
respond only with: 'Content not suitable for posting'.
"""


def validate_openai_env():
    required_vars = ["OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required OpenAI environment variables: {', '.join(missing)}")


def generate_summary(platform, link, max_graphemes=300, max_retries=3):
    validate_openai_env()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    output = None
    for attempt in range(1, max_retries + 1):
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=POST_INSTRUCTIONS_TEMPLATE.format(platform=platform),
            tools=[{"type": "web_search_preview"}],
            input=link
        )
        output = response.output_text.strip()
        if output == "Content not suitable for posting":
            print("[OpenAI] Content flagged as unsuitable for posting. Skipping.")
            return None
        if grapheme.length(output) <= max_graphemes:
            return output
        else:
            print(f"[OpenAI] Output too long ({grapheme.length(output)} graphemes), retrying ({attempt}/{max_retries})...")
    if output is not None:
        graphemes_list = [g for g in grapheme.graphemes(output) if isinstance(g, str) and g is not None]
        truncated = ''.join(graphemes_list[:max_graphemes])
        print(f"[OpenAI] Output still too long after {max_retries} retries, truncating to {max_graphemes} graphemes.")
        return truncated
    else:
        raise RuntimeError("OpenAI did not return any output after retries.")
