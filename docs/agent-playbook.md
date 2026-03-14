# Agent Playbook

## Source Of Truth
- `README.md` explains local run, publishing flow, and repository layout.
- `PRD.md` defines newsroom product rules and REST/publishing contracts.
- `ARCHITECTURE.md` defines ingestion, validation, and publishing responsibilities.
- `AGENT.md` defines editorial roles and operational responsibilities.

## Repository Map
- `_posts/` published articles.
- `data/ready-news/` staged article payloads.
- `scripts/` automation helpers.
- `.github/workflows/` publishing and validation pipelines.
- `assets/`, `_data/`, `_pages/` site presentation and metadata.

## Change Workflow
1. Confirm whether the change affects article schema, workflow, or presentation.
2. Update the relevant source-of-truth docs before or alongside code changes.
3. Keep GitHub Actions behavior consistent with the documented ready-news process.
4. Avoid editing generated post content unless the task explicitly targets published output.

## Validation
- `bundle install`
- `bundle exec jekyll build`
- `bundle exec jekyll serve --host 0.0.0.0`
- If scripts change, run the smallest relevant script-level smoke test.
