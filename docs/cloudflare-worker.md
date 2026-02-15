# Cloudflare Worker Trigger (repository_dispatch)

Cloudflare Workers를 **리모컨 래퍼**로 사용해 `/trigger` 엔드포인트를 제공할 수 있습니다.

## 1) Worker 코드

> 코드 위치: `infra/cloudflare-worker/`

`wrangler.toml`
```toml
name = "aibc-trigger"
main = "src/worker.js"
compatibility_date = "2025-01-01"
```

`src/worker.js`
```js
export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    const body = await request.json().catch(() => ({}));
    const category = body.category;
    if (!category) {
      return new Response("Missing category", { status: 400 });
    }

    const payload = {
      event_type: "publish_article",
      client_payload: {
        category,
        run_date: body.run_date,
        force: Boolean(body.force),
        dry_run: Boolean(body.dry_run),
        idempotency_key: body.idempotency_key,
      },
    };

    const resp = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
      },
      body: JSON.stringify(payload),
    });

    const text = await resp.text();
    return new Response(text, { status: resp.status, headers: { "Content-Type": "application/json" } });
  },
};
```

## 2) Secrets/Env

```
wrangler secret put GITHUB_TOKEN
wrangler secret put GITHUB_REPO
```

## 3) 호출 예시

```bash
curl -X POST https://<your-worker>.workers.dev/trigger \
  -H "Content-Type: application/json" \
  -d '{"category":"economy","run_date":"2026-02-15","force":false}'
```

## 4) 권장 권한

- Fine-grained PAT
- Repository: `Actions` read/write
