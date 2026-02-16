# AIBC News

AI 기반 자동 편집국이 운영하는 **카테고리별 기사 발행** 사이트입니다. Jekyll + Minimal Mistakes 테마를 사용하고, GitHub Actions로 자동 발행을 지원합니다.

## 주요 기능
- 한국어 UI 및 콘텐츠
- 다크 테마 적용 (Minimal Mistakes)
- 카테고리별 뉴스 제공 (정치, 경제, 사회, 세계, 기술, 문화, 스포츠, 연예, 생활, 날씨)
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

GitHub Actions로 **카테고리별 정기 실행**을 구성했습니다.

## 이미지 업로드 (Repo 저장)

이미지는 `/assets/images/`에 저장하고 `image:`에 경로를 사용합니다.

1) 자동 최적화 (GitHub Actions)
- `assets/images/`에 JPG/PNG 업로드하면 자동으로 WEBP로 변환됩니다.

2) 수동 최적화
```bash
python scripts/optimize_image.py <path/to/image.jpg>
```

3) 생성된 파일 경로 사용
```yaml
image: /assets/images/your-image.webp
```

기본 설정: **WEBP, 최대 1200px, 품질 82**

> 내부 카테고리 키(영문): politics, economy, society, world, tech, culture, sports, entertainment, life, weather

1. 워크플로우(`.github/workflows/publish-article-*.yml`) 확인

커밋/푸시는 GitHub Actions 단계에서 수행합니다.

> 제목에 모델명을 표시합니다. (환경변수 `ARTICLE_MODEL_NAME`, 기본값: GPT-5.2)

### REST Trigger (repository_dispatch)

Azure Functions `trigger_publish_article`는 **repository_dispatch를 호출하는 리모컨** 역할만 수행합니다.

**Required env:**
- `GITHUB_TOKEN`
- `GITHUB_REPO` (예: `yeongseon/aibc-news`)

**Request JSON:**
```json
{
  "run_date": "2026-02-15",
  "category": "economy",
  "dry_run": false,
  "force": false,
  "idempotency_key": "2026-02-15-economy-ks11",
  "max_chars": 160,
  "min_chars": 160
}
```

**동작:**
- REST → `repository_dispatch` (event_type: publish_article)
- 실제 발행/커밋은 Actions에서 처리

### External Trigger Recipes

#### curl
```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/yeongseon/aibc-news/dispatches \
  -d '{"event_type":"publish_article","client_payload":{"category":"economy","run_date":"2026-02-15","force":false}}'
```

#### GitHub CLI
```bash
gh api repos/yeongseon/aibc-news/dispatches \
  -f event_type=publish_article \
  -f client_payload.category=economy \
  -f client_payload.run_date=2026-02-15 \
  -F client_payload.force=false
```

#### Python
```python
import requests

url = "https://api.github.com/repos/yeongseon/aibc-news/dispatches"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}
body = {
    "event_type": "publish_article",
    "client_payload": {"category": "economy", "run_date": "2026-02-15", "force": False},
}
requests.post(url, headers=headers, json=body, timeout=15)
```

#### Node.js
```js
import fetch from "node-fetch";

const res = await fetch("https://api.github.com/repos/yeongseon/aibc-news/dispatches", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${process.env.GITHUB_TOKEN}`,
    "Accept": "application/vnd.github+json",
  },
  body: JSON.stringify({
    event_type: "publish_article",
    client_payload: { category: "economy", run_date: "2026-02-15", force: false },
  }),
});
```

### Token 최소 권한 가이드

- **Fine-grained PAT** 권장
- Repository scope: `Actions`(read/write)
- Contents 권한은 불필요 (dispatch만 호출)

## 배포 (GitHub Pages)

1. Repository를 Public으로 전환
2. Settings → Pages에서 `main` 브랜치 `/ (root)` 선택
3. 배포 URL 확인: `https://<username>.github.io/aibc-newsroom/`

## 문서

- 제품 요구사항: `PRD.md`
- 아키텍처: `ARCHITECTURE.md`
- Cloudflare Worker 트리거: `docs/cloudflare-worker.md` (infra/cloudflare-worker/)
- Azure Function 트리거: `docs/azure-function.md` (infra/azure-functions/)

## 라이선스

필요 시 명시해주세요.
