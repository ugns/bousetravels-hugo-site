import feedparser
import os
import time
from datetime import datetime, timezone


def fetch_rss_entries(feed_url):
    feed = feedparser.parse(feed_url)
    return feed.entries


def parse_entry_link_and_date(entry):
    link = entry.get("link", "")
    published_parsed = getattr(entry, "published_parsed", None)
    pub_date = None
    if published_parsed and isinstance(published_parsed, time.struct_time):
        pub_date = datetime.fromtimestamp(time.mktime(published_parsed), tz=timezone.utc)
    return link, pub_date


def load_seen_links(SEEN_FILE, OLD_SEEN_FILE):
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    elif os.path.exists(OLD_SEEN_FILE):
        with open(OLD_SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_seen_links(seen_links, SEEN_FILE):
    with open(SEEN_FILE, "w") as f:
        for link in seen_links:
            f.write(link + "\n")
