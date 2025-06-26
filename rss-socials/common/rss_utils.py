import feedparser
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Set, Tuple, Optional


def fetch_rss_entries(feed_url: str) -> Any:
    """
    Parse the RSS feed and return its entries.

    Args:
        feed_url: The URL of the RSS feed.

    Returns:
        The entries from the parsed feed.
    """
    feed = feedparser.parse(feed_url)
    return feed.entries


def parse_entry_link_and_date(entry: Any) -> Tuple[str, Optional[datetime]]:
    """
    Extract the link and publication date from an RSS entry.

    Args:
        entry: The RSS entry object.

    Returns:
        A tuple of (link, publication datetime or None).
    """
    link = entry.get("link", "")
    published_parsed = getattr(entry, "published_parsed", None)
    pub_date = None
    # Check for 'published_parsed' or 'updated_parsed'
    if not published_parsed:
        published_parsed = getattr(entry, "updated_parsed", None)
    if published_parsed and isinstance(published_parsed, time.struct_time):
        pub_date = datetime.fromtimestamp(time.mktime(published_parsed), tz=timezone.utc)
    return link, pub_date


def load_seen_links(SEEN_FILE: str, OLD_SEEN_FILE: str) -> Set[str]:
    """
    Load the set of seen links from the deduplication file(s).

    Args:
        SEEN_FILE: Path to the current deduplication file.
        OLD_SEEN_FILE: Path to the legacy deduplication file.

    Returns:
        A set of seen links.
    """
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    elif os.path.exists(OLD_SEEN_FILE):
        with open(OLD_SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_seen_links(seen_links: Set[str], SEEN_FILE: str) -> None:
    """
    Save the set of seen links to the deduplication file.

    Args:
        seen_links: Set of links to save.
        SEEN_FILE: Path to the deduplication file.
    """
    with open(SEEN_FILE, "w") as f:
        for link in seen_links:
            f.write(link + "\n")
