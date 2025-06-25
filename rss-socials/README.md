# RSS to Bluesky Automation

This project automates posting new entries from an RSS feed to Bluesky, generating rich social cards with Open Graph metadata and deduplication. It is designed for scheduled or CI/CD-driven workflows (e.g., GitHub Actions).

## Features
- **RSS Parsing:** Fetches and parses entries from a configured RSS feed.
- **Deduplication:** Tracks already-posted links to avoid reposting.
- **Summary Generation:** Uses OpenAI's API to generate a short, hashtagged teaser for each new entry.
- **Metadata Extraction:** Fetches the linked page and parses Open Graph/meta tags for title, description, and image (handles relative URLs).
- **Bluesky Posting:** Posts to Bluesky using the atproto client, tagging hashtags and linking URLs in the message. If an image is found, it uploads it as a blob and attaches it as a social card thumbnail.
- **Error Handling:** Robust error handling for network, API, and posting errors.
- **Workflow Ready:** Designed for automation, with all config via environment variables.

## Requirements
- Python 3.8+
- Bluesky account and app password
- OpenAI API key
- RSS feed URL

## Installation

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install feedparser openai atproto requests beautifulsoup4
   ```

## Configuration
Set the following environment variables (in your CI/CD secrets or locally):
- `RSS_FEED_URL`: The URL of your RSS feed.
- `BLUESKY_HANDLE`: Your Bluesky handle (e.g., `user.bsky.social`).
- `BLUESKY_APP_PASSWORD`: Your Bluesky app password.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `SEEN_FILE`: (Optional) Path to the file used for deduplication. Defaults to `seen_rss_posts.txt` if not set.

## Usage

Run the script manually:
```bash
python rss-socials/rss-to-social.py
```

Or use the provided GitHub Actions workflow for scheduled/automated runs.

## How It Works
1. **Fetches RSS entries** and loads the set of already-posted links.
2. **For each new entry** (not seen and published within the last 7 days):
   - Generates a summary using OpenAI.
   - Fetches page metadata (title, description, image) for a social card.
   - Uploads the image as a blob to Bluesky (if available).
   - Posts to Bluesky with hashtags, links, and a rich card.
   - Marks the link as seen.

## Customization
- Edit the prompt in `generate_summary()` to change the style or length of the generated post.
- Adjust the deduplication logic or time window as needed.

## Troubleshooting
- Ensure all required environment variables are set.
- Check the logs for errors related to network, authentication, or API limits.
- The script prints skipped/old links and errors for transparency.

## License
MIT
