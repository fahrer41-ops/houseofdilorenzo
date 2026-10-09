interface Env {
  VIEWS: KVNamespace
  ASSETS: Fetcher
}

// Slugs we'll actually count. Anything else gets rejected so the
// endpoint can't be used as an open counter for arbitrary keys.
const KNOWN_SLUGS = new Set([
  'series-ep1',
  'film-rise-of-an-empire-siege',
  'film-start-of-forever',
])

function jsonResponse(body: unknown, init?: ResponseInit) {
  return new Response(JSON.stringify(body), {
    ...init,
    headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) },
  })
}

async function handleViews(request: Request, env: Env, slug: string): Promise<Response> {
  if (!KNOWN_SLUGS.has(slug)) {
    return jsonResponse({ error: 'unknown slug' }, { status: 404 })
  }

  const key = `views:${slug}`

  if (request.method === 'POST') {
    const current = Number((await env.VIEWS.get(key)) ?? '0')
    const next = current + 1
    await env.VIEWS.put(key, String(next))
    return jsonResponse({ views: next })
  }

  // GET — read-only, no increment.
  const current = Number((await env.VIEWS.get(key)) ?? '0')
  return jsonResponse({ views: current })
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url)
    const match = url.pathname.match(/^\/api\/views\/([a-z0-9-]+)$/)

    if (match) {
      return handleViews(request, env, match[1])
    }

    return env.ASSETS.fetch(request)
  },
}
