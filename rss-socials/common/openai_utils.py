import os
import grapheme
from openai import OpenAI
from typing import Optional

POST_INSTRUCTIONS_TEMPLATE = """
Generate a {platform} post for my latest blog post.

The post must:
- Be under {max_graphemes} graphemes
- Contain no more than three hashtags
- Entice the audience to click on the link without revealing all content

Use an engaging, appropriate tone for {platform}.

If the linked content is inappropriate, offensive, broken, or otherwise unsuitable for public sharing,
respond only with: 'Content not suitable for posting'.
"""


def validate_openai_env() -> None:
    """Raise an error if required OpenAI environment variables are missing."""
    required_vars = ["OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required OpenAI environment variables: {', '.join(missing)}")


def generate_summary(
    platform: str,
    link: str,
    max_graphemes: int = 300,
    max_retries: int = 3
) -> Optional[str]:
    """
    Generate a summary for a blog post using OpenAI, ensuring it fits within a grapheme limit.

    Args:
        platform: The name of the platform (e.g., 'Bluesky').
        link: The URL to summarize.
        max_graphemes: Maximum allowed graphemes in the summary.
        max_retries: Number of times to retry if the summary is too long.

    Returns:
        The generated summary string, or None if content is not suitable for posting.
    Raises:
        EnvironmentError: If the OpenAI API key is missing.
        RuntimeError: If OpenAI does not return any output after retries.
    """
    validate_openai_env()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    output: Optional[str] = None
    for attempt in range(1, max_retries + 1):
        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=POST_INSTRUCTIONS_TEMPLATE.format(platform=platform, max_graphemes=max_graphemes),
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
