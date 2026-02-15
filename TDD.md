# [TDD] AIBC Publish Article Pipeline

**작성일:** 2026-02-12  
**최종 수정:** 2026-02-15  
**상태:** Draft

---

## 1. 목적

AIBC 파이프라인을 **카테고리별 독립 실행** 구조로 설계하고,
GitHub Actions + REST API 병행 발행을 지원한다.

---

## 2. 아키텍처 개요

```
GitHub Actions (cron)           REST (Azure Functions)
        │                              │
        ▼                              ▼
scripts/run_publish_article.py     /api/publish
        │                              │
        ▼                              ▼
src/pipeline.py               repository_dispatch
  ├─ Collector (category)        └─ Actions 실행
  ├─ Writer
  ├─ QualityGate
  └─ Publisher (commit/push)
```

---

## 3. 실행 흐름

### 3.1 Actions
1. GitHub Actions 스케줄 실행
2. `scripts/run_publish_article.py`
3. `pipeline.run_pipeline(category=...)`
4. Collector → Writer → Quality Gate → Publisher
5. `_posts/` 커밋/푸시

### 3.2 REST
1. `POST /api/publish`
2. repository_dispatch 트리거
3. Actions가 파이프라인 실행 및 `_posts/` 반영

---

## 4. 데이터 스키마

```json
{
  "date": "YYYY-MM-DD",
  "items": [
    {
      "type": "headline|market|weather|lifestyle",
      "title": "...",
      "facts": ["...", "..."],
      "sources": [
        {"name": "기관/매체", "url": "https://...", "published_at": "YYYY-MM-DD"}
      ]
    }
  ]
}
```

---

## 5. 파일 규칙

- 파일명: `YYYY-MM-DD-<category>-<slug>.md`
- 멱등성: 기본 skip, `force=true` 시 overwrite

---

## 6. REST API

`POST /api/publish`

```json
{
  "run_date": "2026-02-15",
  "category": "market",
  "force": false,
  "idempotency_key": "2026-02-15-market-ks11"
}
```

---

## 7. GitHub Actions

카테고리별 워크플로 구성:
- `publish-article-market.yml`
- `publish-article-weather.yml`
- `publish-article-life.yml`
- `publish-article-news.yml`

---

## 8. 오류 처리

- Collector 실패: 최대 2회 재시도
- Writer 실패: 1회 재시도 후 중단
- Quality Gate 실패: 발행 중단
- Publisher 실패: 커밋/푸시 실패 시 중단

---

## 9. 품질 기준

- 2~4문장
- 출처 최소 1개
- 금칙어 미포함
- 수치 포함 시 기준시점/발표일 포함
