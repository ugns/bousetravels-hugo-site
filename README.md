# bousetravels.world Automation & Assets

This repository contains automation and assets for the [bousetravels.world](https://bousetravels.world) project, including:

- **Automated RSS-to-Bluesky posting** via the [`rss2socials`](https://pypi.org/project/rss2socials/) package.
- **Pre-commit hook for image resizing** to ensure all JPGs in `assets/images/` are web/social-media optimized.

---

## Features

### 1. Automated RSS-to-Bluesky Posting

- **Fetches new entries from your RSS feed** and posts them to Bluesky with rich social cards.
- **Deduplication:** Tracks already-posted links to avoid reposting.
- **OpenAI Summarization:** Generates concise, hashtagged summaries for each post.
- **Open Graph Metadata Extraction:** Fetches and attaches title, description, and image as a social card.
- **Configurable via environment variables** for easy CI/CD or scheduled automation.
- **Robust error handling, Unicode support, and modular codebase.**

> The automation is designed to run via GitHub Actions or locally using the `rss2socials` PyPI package.

---

### 2. Pre-commit Hook: JPG Image Resizing

- **Automatically resizes JPGs in `assets/images/`** to a maximum of 1200x630 pixels (maintaining aspect ratio) before every commit.
- **Prevents large images from being committed**, ensuring fast load times and optimal display on social media.
- **Uses [pre-commit](https://pre-commit.com/) for seamless integration with git.**

---

## Quick Local Development Setup

```bash
# Create and activate a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install required packages
pip install --upgrade pip
pip install pre-commit rss2socials pillow

# Install pre-commit hooks
pre-commit install
```

---

## Pre-commit Configuration

This repository uses the following `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: resize-jpgs
        name: Resize JPGs in assets/images
        entry: python assets/images/resize_jpgs.py
        language: system
        files: ^assets/images/.*\.jpg$
        staged: true
```

- The hook will run `assets/images/resize_jpgs.py` on any staged `.jpg` files in `assets/images/` and re-stage them if modified.

---

## Usage

### Automated Social Posting

- The automation is intended to be run via GitHub Actions or a similar scheduler.
- Configure your environment variables (see below) in your CI/CD or local environment.
- The main automation logic is provided by the [`rss2socials`](https://pypi.org/project/rss2socials/) package.

### Image Resizing

- Any time you commit `.jpg` files in `assets/images/`, the pre-commit hook will automatically resize them if needed.
- No manual action is required—just commit as usual!

---

## Environment Variables for Automation

Set the following environment variables for the RSS-to-Bluesky automation:

- `RSS_FEED_URL`: The URL of your RSS feed. **(Required)**
- `BLUESKY_HANDLE`: Your Bluesky handle (e.g., `user.bsky.social`). **(Required)**
- `BLUESKY_APP_PASSWORD`: Your Bluesky app password. **(Required)**
- `OPENAI_API_KEY`: Your OpenAI API key. **(Required)**
- `SEEN_FILE`: (Optional) Path to the file used for deduplication. Defaults to `seen_rss_posts.txt` if not set.
- `POST_AGE_LIMIT_DAYS`: (Optional) Maximum age (in days) for RSS entries to be posted. Defaults to 7 if not set.

---

## Recommendations for Feature Images

- **Recommended size:** 1200x630 pixels (1.91:1 aspect ratio)
- **Recommended file size:** Under 1 MB (ideally 200–500 KB)
- **Format:** JPEG

The pre-commit hook will help enforce these recommendations automatically.

---

## License

MIT

---

## Contributing

1. Fork and clone the repo.
2. Set up your Python environment and install pre-commit as described above.
3. Make your changes and commit—image resizing will happen automatically!
4. Open a pull request.

---

## Questions?

Open an issue or contact the maintainer via [bousetravels.world](https://bousetravels.world).