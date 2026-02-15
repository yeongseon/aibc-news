# Azure Function Trigger (repository_dispatch)

Azure Function은 **repository_dispatch를 호출하는 리모컨** 역할만 수행합니다.

> 코드 위치: `infra/azure-functions/`

## 1) 환경 변수
- `GITHUB_TOKEN`
- `GITHUB_REPO` (예: `yeongseon/aibc-news`)

## 2) 요청 JSON
```json
{
  "run_date": "2026-02-15",
  "category": "economy",
  "force": false,
  "dry_run": false,
  "idempotency_key": "2026-02-15-economy-ks11"
}
```

## 3) 동작
- REST → `repository_dispatch` (event_type: publish_article)
- 실제 발행/커밋은 Actions에서 처리

## 4) 권장 권한
- Fine-grained PAT
- Repository: `Actions` read/write
