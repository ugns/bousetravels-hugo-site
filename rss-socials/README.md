# RSS to Bluesky Automation

This project automates posting new entries from an RSS feed to Bluesky, generating rich social cards with Open Graph metadata and deduplication. It is designed for scheduled or CI/CD-driven workflows (e.g., GitHub Actions).

## Features

- **RSS Parsing:** Fetches and parses entries from a configured RSS feed.
- **Deduplication:** Tracks already-posted links to avoid reposting, with configurable file location and legacy fallback.
- **Summary Generation:** Uses OpenAI's API to generate a short, hashtagged teaser for each new entry, with Unicode grapheme counting and retry logic.
- **Metadata Extraction:** Fetches the linked page and parses Open Graph/meta tags for title, description, and image (handles relative URLs).
- **Bluesky Posting:** Posts to Bluesky using the atproto client, tagging hashtags and linking URLs in the message. If an image is found, it uploads it as a blob and attaches it as a social card thumbnail.
- **Environment Validation:** Fails fast if required environment variables are missing (for main, OpenAI, and Bluesky).
- **Error Handling:** Robust error handling for network, API, and posting errors.
- **Workflow Ready:** Designed for automation, with all config via environment variables and dependency pinning for reproducible builds.
- **Modular Codebase:** All logic is split into reusable modules for maintainability and testability.

## Requirements

- Python 3.8+
- Bluesky account and app password
- OpenAI API key
- RSS feed URL
- The following Python packages (see `requirements.txt` for pinned versions):
  - `feedparser`
  - `openai`
  - `atproto`
  - `requests`
  - `trafilatura`
  - `lxml`
  - `grapheme`

## Installation

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r rss-socials/requirements.txt
   ```

## Configuration

Set the following environment variables (in your CI/CD secrets or locally):

- `RSS_FEED_URL`: The URL of your RSS feed. **(Required)**
- `BLUESKY_HANDLE`: Your Bluesky handle (e.g., `user.bsky.social`). **(Required)**
- `BLUESKY_APP_PASSWORD`: Your Bluesky app password. **(Required)**
- `OPENAI_API_KEY`: Your OpenAI API key. **(Required)**
- `SEEN_FILE`: (Optional) Path to the file used for deduplication. Defaults to `seen_rss_posts.txt` if not set.
- `POST_AGE_LIMIT_DAYS`: (Optional) Maximum age (in days) for RSS entries to be posted. Defaults to 7 if not set.

## Usage

Run the script manually:
```bash
python rss-socials/rss-to-bluesky.py
```

Or use the provided GitHub Actions workflow for scheduled/automated runs.

## How It Works

1. **Validates environment variables** for all required services (main, OpenAI, Bluesky).
2. **Fetches RSS entries** and loads the set of already-posted links (with legacy fallback).
3. **For each new entry** (not seen and published within the last `POST_AGE_LIMIT_DAYS`):
   - Generates a summary using OpenAI, with grapheme counting and retries. If OpenAI returns `Content not suitable for posting`, the entry is skipped and not marked as seen.
   - Fetches page metadata (title, description, image) for a social card.
   - Uploads the image as a blob to Bluesky (if available).
   - Posts to Bluesky with hashtags, links, and a rich card.
   - Marks the link as seen.

## Customization

- Edit the `POST_INSTRUCTIONS_TEMPLATE` variable in `common/openai_utils.py` to change the style, length, or requirements of the generated post prompt for OpenAI.
- Adjust the deduplication logic or time window as needed by modifying the relevant utility functions.

## Troubleshooting

- Ensure all required environment variables are set.
- Check the logs for errors related to network, authentication, or API limits.
- The script prints skipped/old links and errors for transparency.
- For CI/CD, ensure secrets and environment variables are properly configured in your workflow.

## License

MIT
