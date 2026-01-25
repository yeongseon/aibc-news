---
name: Architecture Implementation
about: Implement Phase 1 pipeline per ARCHITECTURE.md
title: "[Architecture] "
labels: ["architecture", "phase-1"]
assignees: ""
---

## Summary

## Scope Checklist
- [ ] Scheduler (GitHub Actions) runs daily at 06:30 KST
- [ ] Collector implemented with schema and retry policy
- [ ] Writer implemented with markdown output rules
- [ ] Quality Gate validations implemented
- [ ] Publisher generates front matter and _posts output
- [ ] Storage layout created (data/, logs/, src/)
- [ ] Secrets configured (LLM API, data sources)
- [ ] Tests added for collector/writer/quality/publisher

## Interfaces
- Collector JSON schema aligns with ARCHITECTURE.md
- Writer markdown format aligns with ARCHITECTURE.md
- Publisher front matter aligns with ARCHITECTURE.md

## Quality Gate Criteria
- 700 to 1000 characters
- 3 to 5 items, 2 to 4 sentences each
- 2 to 3 context sentences per item
- Sources: min 1 per item, total 4+
- Same source <= 50%
- No banned words or exaggeration
- Quotes and numbers include dates or reference times

## Data Sources
- List APIs or official sources used

## Risks / Open Questions

## Acceptance Criteria
- Passes all quality gate checks
- No partial publish on failure
- Idempotent rerun by date
- Output matches front matter and post schema
