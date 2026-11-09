import { useEffect, useState } from 'react'

type Props = {
  slug: string
  className?: string
}

export default function ViewCounter({ slug, className }: Props) {
  const [views, setViews] = useState<number | null>(null)

  useEffect(() => {
    let cancelled = false
    const sessionKey = `viewed:${slug}`

    async function load() {
      try {
        const alreadyCounted = sessionStorage.getItem(sessionKey) === '1'
        const res = await fetch(`/api/views/${slug}`, {
          method: alreadyCounted ? 'GET' : 'POST',
        })
        if (!res.ok) return
        const data = (await res.json()) as { views: number }
        if (!cancelled) setViews(data.views)
        if (!alreadyCounted) sessionStorage.setItem(sessionKey, '1')
      } catch {
        // Counter is a nice-to-have, not essential — fail silently.
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [slug])

  if (views === null) return null

  return (
    <p className={`font-body text-xs tracking-wide text-ivory-dim ${className ?? ''}`}>
      {views.toLocaleString()} {views === 1 ? 'view' : 'views'}
    </p>
  )
}
