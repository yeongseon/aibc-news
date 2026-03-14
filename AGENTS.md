# AGENTS.md

## Purpose
`aibc-news` is a Jekyll-based automated newsroom that publishes category-specific articles from structured ready-news inputs.

## Read First
- `README.md`
- `PRD.md`
- `ARCHITECTURE.md`
- `AGENT.md`
- `docs/agent-playbook.md`

## Working Rules
- Keep publishing contracts, ready-news schema, and site behavior aligned.
- If workflow semantics change, update both product docs and automation docs in the same change.
- Preserve category slugs, file naming rules, and idempotent publishing behavior unless intentionally redesigning them.
- Prefer edits that keep generated content separate from the publishing engine.

## Validation
- `bundle exec jekyll build`
- If site behavior changes locally, also test `bundle exec jekyll serve --host 0.0.0.0`
