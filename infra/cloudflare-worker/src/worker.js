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
        max_chars: body.max_chars,
        min_chars: body.min_chars,
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
