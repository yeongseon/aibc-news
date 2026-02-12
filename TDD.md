# [TDD] AIBC Daily Brief Pipeline

**작성일:** 2026-02-12  
**상태:** Draft

---

## 1. 목적

AIBC의 Daily Brief 파이프라인을 **Collector → Writer → Publisher**로 분리하고,
정해진 시간에 자동 발행되는 안정적인 운영 구조를 정의한다.

---

## 2. 아키텍처 개요

```
GitHub Actions (cron)
        │
        ▼
run_daily_brief.py
        │
        ▼
src/pipeline.py
  ├─ Collector (data/*)
  ├─ Writer (markdown)
  ├─ QualityGate (검증)
  └─ Publisher (_posts)
```

### 구성 요소
- **Collector**: 데이터 수집 후 `data/collector/YYYY-MM-DD.json` 저장
- **Writer**: Collector 결과 → 마크다운 본문 생성
- **QualityGate**: 분량/문장/출처/금칙어 검사
- **Publisher**: `_posts/YYYY-MM-DD-aibc-briefing.md` 생성 및 저장
- **Logs**: `logs/YYYY-MM-DD.log`에 단계별 기록

---

## 3. 실행 흐름 (Sequence)

1. GitHub Actions 스케줄(06:30 KST)이 트리거됨
2. `scripts/run_daily_brief.py` 실행
3. `pipeline.run_pipeline()` 호출
4. Collector 실행 (재시도 포함)
5. Writer 실행
6. QualityGate 검증
7. Publisher 실행
8. `_posts/`, `data/`, `logs/` 커밋 및 푸시

---

## 4. 데이터 스키마

### Collector 출력
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

### 품질 검사 결과
```json
{
  "pass": true,
  "reasons": [],
  "metrics": {
    "char_count": 850,
    "item_count": 4,
    "sources_total": 5,
    "sources_unique": 4
  }
}
```

---

## 5. 파일 구조

```
.
├─ _posts/                         # 발행 결과
├─ data/
│  ├─ collector/YYYY-MM-DD.json    # 수집 결과
│  └─ quality/YYYY-MM-DD.json      # 품질 검사 결과
├─ logs/YYYY-MM-DD.log             # 파이프라인 로그
├─ scripts/
│  ├─ run_daily_brief.py
│  └─ generate_news.py
├─ src/
│  ├─ collector/
│  ├─ writer/
│  ├─ quality/
│  ├─ publisher/
│  └─ pipeline.py
```

---

## 6. GitHub Actions

### daily-brief.yml
- **schedule:** `cron: "30 21 * * *"` (06:30 KST)
- **workflow_dispatch:** 수동 실행
  - `run_date` (YYYY-MM-DD)
  - `dry_run` (true/false)

### 환경 변수
- `OPENAI_API_KEY` (LLM용, TBD)
- `RUN_DATE` (optional)
- `DRY_RUN` (optional)

---

## 7. 오류 처리

- Collector 실패: 최대 2회 재시도
- Writer 실패: 1회 재시도 후 중단
- QualityGate 실패: 발행 중단 및 실패 사유 기록
- Publisher 실패: 이전 상태 유지, 실패 로그 저장

**원칙:** 부분 발행 금지

---

## 8. 품질 기준 (Quality Gate)

- 분량 700~1,000자
- 항목 3~5개
- 항목당 2~4문장
- 출처 최소 4개, 동일 출처 50% 초과 금지
- 금칙어 불포함
- 수치 포함 시 발표일/기준시점 표기

---

## 9. 확장 설계 (Phase 2+)

- 다중 Writer (섹션별 Writer 분리)
- 데이터 분석 섹션 추가
- 후속 검수 단계(요약/중복 검사)

---

## 10. TBD

1. Collector 실제 API 소스 확정 (주식: Yahoo Finance, 날씨: OpenWeather)
2. Writer LLM 공급자 및 모델 확정 (GitHub Copilot: gpt-4o)
3. 실패 알림 채널 (GitHub Issue)
4. 다국어 지원 여부 (KR only)

