import feedparser
import os
from openai import OpenAI
from datetime import datetime, timezone, timedelta
from atproto import Client, DidInMemoryCache, IdResolver

# --- CONFIGURATION ---
RSS_FEED_URL = os.getenv("RSS_FEED_URL")
SEEN_FILE = ".github/seen_rss_posts.txt"


# --- FUNCTIONS ---
def fetch_rss_entries(feed_url):
    feed = feedparser.parse(feed_url)
    return feed.entries


def generate_summary(platform, link):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=f"You are writing a social media post on {platform} for the following link",
        input=link
    )
    return response.output_text.strip()


def post_to_bluesky(message, link):
    handle = os.getenv("BLUESKY_HANDLE")
    app_password = os.getenv("BLUESKY_APP_PASSWORD")
    if not handle or not app_password:
        raise ValueError("Bluesky credentials not set in environment variables")
    try:
        cache = DidInMemoryCache()
        resolver = IdResolver(cache=cache)
        did = resolver.did.resolve(resolver.handle.resolve(handle))  # type: ignore
        client = Client(base_url=did.get_pds_endpoint()) if did.get_pds_endpoint() else Client()  # type: ignore
        client.login(handle, app_password)
        # Only append the link if it's not already in the message
        post_text = f"{message}\n\n{link}" if link and link not in message else message
        client.send_post(text=post_text)
        print(f"[Bluesky] Posted: {post_text}")
    except Exception as e:
        print(f"[Bluesky] Error posting to Bluesky: {e}")
        raise


def load_seen_links():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_seen_links(seen_links):
    with open(SEEN_FILE, "w") as f:
        for link in seen_links:
            f.write(link + "\n")


def main():
    entries = fetch_rss_entries(RSS_FEED_URL)
    seen_links = load_seen_links()
    now = datetime.now(timezone.utc)
    for entry in entries:
        link = entry.get("link", "")
        pub_date = None
        pub_date_str = entry.get("pubDate", "")
        if pub_date_str:
            try:
                pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")  # type: ignore
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                else:
                    pub_date = pub_date.astimezone(timezone.utc)
            except (AttributeError, TypeError, ValueError):
                pub_date = None
        else:
            pub_date = None

        if link and link not in seen_links and pub_date and (now - pub_date) < timedelta(days=7):  # type: ignore
            try:
                bluesky_msg = generate_summary("Bluesky", link)
                post_to_bluesky(bluesky_msg, link)
                if isinstance(link, str):
                    seen_links.add(link)
                    save_seen_links(seen_links)
            except Exception as e:
                print(f"Error posting {link}: {e}")
                # Optionally, continue to next link or break


if __name__ == "__main__":
    main()
