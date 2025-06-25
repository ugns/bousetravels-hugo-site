import feedparser
import os
import time
import requests
from openai import OpenAI
from datetime import datetime, timezone, timedelta
from atproto import Client, DidInMemoryCache, IdResolver, client_utils, models
from urllib.parse import urlparse
from pprint import pprint
from bs4 import BeautifulSoup

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
        instructions=f"You are writing a short teaser social media post on {platform} for the following link. It must not be longer than 300 graphemes with no more than three hashtags. If the content is not suitable for posting, respond with 'Content not suitable for posting'.",
        input=link
    )
    return response.output_text.strip()


def parse_hashtags_and_links(message):
    """Builds a TextBuilder object, tagging hashtags and linking URLs in the message, plus the main link if provided."""
    import re
    tb = client_utils.TextBuilder()
    last_idx = 0
    for match in re.finditer(r"#\w+|https?://[\w\.-]+(?:/[\w\./?%&=\-]*)?", message):
        start, end = match.span()
        if start > last_idx:
            tb.text(message[last_idx:start])
        token = message[start:end]
        if token.startswith('#'):
            tb.tag(token, token.lstrip('#'))
        elif token.startswith('http'):
            hostname = urlparse(token).hostname or token
            tb.link(hostname, token)
        last_idx = end
    if last_idx < len(message):
        tb.text(message[last_idx:])
    return tb


def fetch_page_metadata(url, timeout=10):
    """Fetches title, description, and image from a web page for social card."""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Try Open Graph first
        def get_meta_content(tag):
            return tag["content"] if tag and tag.has_attr("content") and isinstance(tag["content"], str) else ""
        title = get_meta_content(soup.find("meta", property="og:title"))
        if not title:
            title_el = soup.find("title")
            title = title_el.text.strip() if title_el else ""
        desc = get_meta_content(soup.find("meta", property="og:description"))
        if not desc:
            desc_tag2 = soup.find("meta", attrs={"name": "description"})
            desc = get_meta_content(desc_tag2)
        image = get_meta_content(soup.find("meta", property="og:image"))
        return str(title), str(desc), str(image)
    except Exception as e:
        print(f"[Metadata] Error fetching metadata for {url}: {e}")
        return "", "", ""


def create_bluesky_embed(link, title, desc, image, client):
    """Create a Bluesky external embed with optional image blob."""
    thumb_blob = None
    if image:
        try:
            img_resp = requests.get(image, timeout=10)
            img_resp.raise_for_status()
            upload_result = client.upload_blob(img_resp.content)
            # Only use if the result is a BlobRef (has 'ref' attribute and not a Response)
            if hasattr(upload_result, 'ref') and 'Response' not in str(type(upload_result)):
                thumb_blob = upload_result
            elif hasattr(upload_result, 'blob'):
                thumb_blob = upload_result.blob
            else:
                thumb_blob = None
        except Exception as img_err:
            print(f"[Bluesky] Error uploading image blob: {img_err}")
            thumb_blob = None
    try:
        embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=link,
                title=title or "",
                description=desc or "",
                thumb=thumb_blob if (thumb_blob is not None and hasattr(thumb_blob, 'ref')) else None
            )
        )
    except Exception as embed_err:
        print(f"[Bluesky] Error creating embed: {embed_err}")
        embed = None
    return embed


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
        post_text = f"{message}\n\n{link}" if link and link not in message else message
        tb = parse_hashtags_and_links(message)
        # Fetch metadata for the social card
        title, desc, image = fetch_page_metadata(link)
        embed = create_bluesky_embed(link, title, desc, image, client)
        if embed:
           client.send_post(tb, embed=embed)
        else:
           client.send_post(tb)
        print(f"[Bluesky] Posted: {tb.build_text()}")
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


def parse_entry_link_and_date(entry):
    link = entry.get("link", "")
    published_parsed = getattr(entry, "published_parsed", None)
    pub_date = None
    if published_parsed and isinstance(published_parsed, time.struct_time):
        pub_date = datetime.fromtimestamp(time.mktime(published_parsed), tz=timezone.utc)
    return link, pub_date


def main():
    entries = fetch_rss_entries(RSS_FEED_URL)
    seen_links = load_seen_links()
    now = datetime.now(timezone.utc)
    for entry in entries:
        link, pub_date = parse_entry_link_and_date(entry)
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
        else:
            print(f"Skipping already seen or old link: {link}")


if __name__ == "__main__":
    main()
