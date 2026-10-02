import { useEffect, useRef } from 'react'
import crestIcon from '../assets/crest-icon.png'
import bannerPoster from '../assets/series-banner-poster.jpg'
import TipCallout from './TipCallout'

const SERIES_TITLE = 'Rise of an Empire'
const SERIES_SEASON = 'Season 1 — House of Di Lorenzo'
const SERIES_TAGLINE = 'Episodes you won’t find anywhere else.'

type Episode = {
  id: string
  number: number
  title: string
  videoId: string
}

// Cloudflare Stream — same account as the rest of the site's hosting.
const STREAM_CUSTOMER_CODE = 'ppcygtjv41676m0o'

const episodes: Episode[] = [
  {
    id: 'ep1',
    number: 1,
    title: 'Rise of an Empire: The Valkyrie’s Vow - Episode 1',
    videoId: '3ef0ad11e2d610207d9e2ef3dd004a1d',
  },
]

function streamEmbedSrc(videoId: string) {
  const poster = encodeURIComponent(
    `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/thumbnails/thumbnail.jpg?time=&height=600`,
  )
  return `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/iframe?poster=${poster}`
}

export default function Series() {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    document.title = `${SERIES_TITLE} — House of Di Lorenzo`
  }, [])

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!prefersReducedMotion) {
      videoRef.current?.play().catch(() => {
        // Autoplay can be blocked by the browser; the poster frame stands in fine.
      })
    }
  }, [])

  return (
    <div className="min-h-screen bg-void">
      <section className="relative flex min-h-[70vh] items-center justify-center overflow-hidden">
        <div className="absolute inset-0">
          <video
            ref={videoRef}
            poster={bannerPoster}
            muted
            loop
            playsInline
            preload="auto"
            className="h-full w-full object-cover object-center"
          >
            <source src="/series-banner.webm" type="video/webm" />
            <source src="/series-banner.mp4" type="video/mp4" />
          </video>
          <div className="absolute inset-0 bg-gradient-to-b from-void/80 via-void/55 to-void" />
          <div className="absolute inset-0 bg-void/25" />
        </div>

        <div className="relative z-10 mx-auto flex max-w-3xl flex-col items-center px-6 py-24 text-center">
          <img src={crestIcon} alt="" className="mb-8 h-16 w-16 object-contain opacity-95" />
          <p className="eyebrow mb-4">House of Di Lorenzo Productions</p>
          <h1 className="font-display text-4xl leading-[1.1] text-ivory sm:text-5xl md:text-6xl">
            {SERIES_TITLE}
          </h1>
          <p className="mt-3 font-display text-lg text-gold-bright italic sm:text-xl">{SERIES_SEASON}</p>
          <p className="mt-5 max-w-xl font-body text-lg text-ivory-dim italic">{SERIES_TAGLINE}</p>
          <p className="mt-6 text-xs tracking-[0.14em] text-gold-dim uppercase">
            Mature themes · Intended for adult audiences
          </p>
        </div>
      </section>

      <section className="px-6 py-20 sm:px-10">
        <div className="mx-auto flex max-w-3xl flex-col gap-14">
          {episodes.map((ep) => (
            <article key={ep.id} className="reveal is-visible">
              <p className="eyebrow mb-3">Episode {ep.number}</p>
              <h2 className="mb-5 font-display text-2xl text-ivory sm:text-3xl">{ep.title}</h2>
              <div className="relative aspect-video w-full overflow-hidden border border-ink-line bg-ink">
                <iframe
                  src={streamEmbedSrc(ep.videoId)}
                  loading="lazy"
                  className="absolute inset-0 h-full w-full border-0"
                  allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                  allowFullScreen
                  title={ep.title}
                />
              </div>
            </article>
          ))}

          <TipCallout />
        </div>
      </section>

      <footer className="border-t border-ink-line px-6 py-10 text-center">
        <a href="/" className="font-body text-sm text-gold underline underline-offset-4">
          Back to House of Di Lorenzo
        </a>
      </footer>
    </div>
  )
}
