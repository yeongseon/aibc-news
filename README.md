# AIBC News

AI 기반 자동 편집국이 운영하는 데일리 뉴스 브리핑 사이트입니다. Jekyll + Minimal Mistakes 테마를 사용하고, GitHub Actions로 자동 발행을 지원합니다.

## 주요 기능
- 한국어 UI 및 콘텐츠
- 다크 테마 적용 (Minimal Mistakes)
- 카테고리별 뉴스 제공 (뉴스, 생활, 날씨, 정책)
- RSS 피드 제공 (`/feed.xml`)
- 자동 뉴스 생성 스크립트 (`scripts/generate_news.py`)

## 빠른 시작

### 1) 로컬 실행
```bash
bundle install
bundle exec jekyll serve --host 0.0.0.0
```

### 2) 빌드
```bash
bundle exec jekyll build
```

## 디렉터리 구조
- `_config.yml`: 사이트 설정
- `_pages/`: 고정 페이지(소개, 정책 등)
- `_posts/`: 뉴스 포스트
- `_data/`: 내비게이션 및 UI 텍스트
- `assets/`: 스타일/스크립트
- `scripts/`: 자동 뉴스 생성 스크립트

## 자동 발행

GitHub Actions로 정기 실행을 구성했습니다. 자동 발행을 사용하려면 다음을 설정하세요.

1. GitHub Secrets에 `OPENWEATHER_API_KEY` 추가
2. 워크플로우(`.github/workflows/daily-brief.yml`) 확인

### REST Trigger (workflow_dispatch)

Azure Functions `trigger_daily_brief`에서 REST 호출로 Actions를 트리거합니다.

**Required env:**
- `GITHUB_TOKEN`
- `GITHUB_REPO` (예: `yeongseon/aibc-news`)
- `WORKFLOW_ID` (default: `daily-brief.yml`)

**Request JSON:**
```json
{
  "run_date": "2026-02-15",
  "dry_run": false,
  "force_publish": false,
  "idempotency_key": "2026-02-15-market-ks11"
}
```

**동작:**
- REST → `workflow_dispatch`
- 발행 로직은 Actions 한 곳만 사용
- 파일명 규칙 기반 멱등성 (기본 skip, `force_publish=true` 시 overwrite)

## 배포 (GitHub Pages)

1. Repository를 Public으로 전환
2. Settings → Pages에서 `main` 브랜치 `/ (root)` 선택
3. 배포 URL 확인: `https://<username>.github.io/aibc-newsroom/`

## 문서

- 제품 요구사항: `PRD.md`
- 아키텍처: `ARCHITECTURE.md`

## 라이선스

필요 시 명시해주세요.
