import os
from datetime import datetime, timezone, timedelta
from common.rss_utils import fetch_rss_entries, parse_entry_link_and_date, load_seen_links, save_seen_links
from common.openai_utils import generate_summary
from common.metadata import fetch_page_metadata
from connectors.bluesky import post_to_bluesky

# --- CONFIGURATION ---
RSS_FEED_URL = os.getenv("RSS_FEED_URL")
SEEN_FILE = os.getenv("SEEN_FILE", "seen_rss_posts.txt")
OLD_SEEN_FILE = ".github/seen_rss_posts.txt"
POST_AGE_LIMIT_DAYS = int(os.getenv("POST_AGE_LIMIT_DAYS", "7"))


def main():
    entries = fetch_rss_entries(RSS_FEED_URL)
    seen_links = load_seen_links(SEEN_FILE, OLD_SEEN_FILE)
    now = datetime.now(timezone.utc)
    for entry in entries:
        link, pub_date = parse_entry_link_and_date(entry)
        is_new_link = link and link not in seen_links
        is_recent = pub_date and (now - pub_date) < timedelta(days=POST_AGE_LIMIT_DAYS)
        if is_new_link and is_recent:
            try:
                bluesky_msg = generate_summary("Bluesky", link)
                if bluesky_msg is None:
                    print(f"Skipping posting for {link} due to OpenAI content filter.")
                    continue
                post_to_bluesky(bluesky_msg, link, fetch_page_metadata)
                if isinstance(link, str):
                    seen_links.add(link)
                    save_seen_links(seen_links, SEEN_FILE)
            except Exception as e:
                print(f"Error posting {link}: {e}")
        else:
            print(f"Skipping already seen or old link: {link}")


if __name__ == "__main__":
    main()
