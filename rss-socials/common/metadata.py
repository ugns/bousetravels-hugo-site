import trafilatura
from lxml import html
from urllib.parse import urljoin
from typing import Optional, Dict


def fetch_page_metadata(url: str) -> Optional[Dict[str, str]]:
    """
    Fetch Open Graph metadata from a given URL using trafilatura for fetching
    and lxml for parsing the HTML content.

    Args:
        url: The URL of the page to fetch metadata from.
    Returns:
        A dictionary of Open Graph metadata, or None if the fetch fails.
    """
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    try:
        tree = html.fromstring(downloaded)
        og_data = {}
        for meta in tree.xpath('//meta'):
            property_attr = meta.attrib.get('property') or meta.attrib.get('name')
            if property_attr and property_attr.startswith('og:'):
                content = meta.attrib.get('content')
                if content:
                    if property_attr == 'og:image':
                        content = urljoin(url, content)
                    if property_attr == 'og:url':
                        content = urljoin(url, content)
                    og_data[property_attr] = content
        return og_data if og_data else None
    except Exception as e:
        print(f"Error parsing metadata: {e}")
        return None
