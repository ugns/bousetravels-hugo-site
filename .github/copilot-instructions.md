# Copilot Coding Agent Instructions for bousetravels.world

This repository powers the bousetravels.world site, combining Hugo static site generation, image asset automation, and social media posting workflows. Follow these guidelines for effective AI coding agent contributions:

## Architecture Overview
- **Hugo-based site**: Content in `content/`, configuration in `config/`, theme assets in `assets/`, and archetypes in `archetypes/`.
- **Image automation**: Pre-commit hook (see `.pre-commit-config.yaml`) runs `assets/images/resize_jpgs.py` to resize JPGs in `assets/images/` before commit.
- **Social automation**: GitHub Actions (`.github/workflows/rss-to-socials.yml`) uses the `rss2socials` Python package to post RSS feed updates to Bluesky, with OpenAI-powered summaries and deduplication.
- **Infrastructure**: Terraform files in `terraform/` manage AWS Amplify deployment, custom domains, and scheduled redeploy Lambda (see `amplify_redeploy_lambda.py`).

## Developer Workflows
- **Local development**: Use `python3 -m venv .venv && source .venv/bin/activate` and install dependencies (`pip install pre-commit rss2socials pillow`).
- **Image handling**: Commit JPGs in `assets/images/` as usual; resizing is automatic via pre-commit.
- **Build/serve site**: Use `npm run dev` for local Hugo server, or `npm run prod` for production-like build.
- **CI/CD**: Amplify build steps are defined in `amplify.yml` (Dart Sass, Go, Hugo, Node.js setup). Output is in `public/`.
- **Social posting**: Configure environment variables for RSS/Bluesky automation (see README). Action runs daily and on demand.
- **Terraform**: Infrastructure changes require PRs to `main` and are applied via GitHub Actions. AWS credentials are managed via OIDC roles.

## Project-Specific Conventions
- **Content front matter**: Use YAML for blog posts (see `archetypes/blog.md` for template).
- **Feature images**: Recommended size is 1200x630px, JPEG format, <1MB. Pre-commit enforces this.
- **Branching**: Main production branch is `main`; feature branches are used for drafts and PRs.
- **Hugo config**: Multi-environment config in `config/` (default, development, production).
- **Automation scripts**: Python scripts for image and deployment automation are in relevant asset or terraform folders.

## Integration Points & Dependencies
- **rss2socials**: Posts RSS updates to Bluesky, uses OpenAI for summaries.
- **AWS Amplify**: Hosts the site, managed via Terraform.
- **Pre-commit**: Handles image resizing.
- **Node.js/NPM**: Used for theme asset management and Hugo build scripts.
- **Dart Sass, Go, Hugo**: Installed in CI/CD via `amplify.yml`.

## Examples & Patterns
- See `assets/images/resize_jpgs.py` for image automation logic.
- See `.github/workflows/rss-to-socials.yml` for social posting workflow.
- See `terraform/amplify_redeploy_lambda.py` for scheduled redeploy logic.
- See `archetypes/blog.md` for content structure.

## Quick Start
- Clone repo, set up Python environment, install pre-commit hooks.
- Use `npm run dev` to serve locally.
- Commit images and content as usual; automation will handle resizing and social posting.

---

If any section is unclear or missing key details, please provide feedback for further refinement.
