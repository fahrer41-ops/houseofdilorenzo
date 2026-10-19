import { useEffect } from 'react'
import crestIcon from '../assets/crest-icon.png'
import TipCallout from './TipCallout'
import ViewCounter from './ViewCounter'

type Film = {
  id: string
  title: string
  videoId: string
  // TODO(Amanda): add a download price here if you want the same
  // paid-download option the Series episodes have (you mentioned
  // $15–20 for a 90-minute film, but hadn't settled on one yet).
  downloadLink?: string
  downloadPrice?: string
}

// Cloudflare Stream — same account as the rest of the site's hosting.
const STREAM_CUSTOMER_CODE = 'ppcygtjv41676m0o'

const films: Film[] = [
  {
    id: 'rise-of-an-empire-siege',
    title: 'Rise of an Empire — The Siege',
    videoId: '7755b7716b64711f1f1106a32ae05696',
    downloadPrice: '$20',
    downloadLink: 'https://ko-fi.com/s/f535616f23',
  },
  {
    id: 'start-of-forever',
    title: 'House of Di Lorenzo — The Start of Forever',
    videoId: '23c167dce29b2512817f47e142d3ac7b',
  },
]

function streamEmbedSrc(videoId: string) {
  const poster = encodeURIComponent(
    `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/thumbnails/thumbnail.jpg?time=&height=600`,
  )
  return `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/iframe?poster=${poster}`
}

export default function Films() {
  useEffect(() => {
    document.title = 'Films — House of Di Lorenzo'
  }, [])

  return (
    <div className="min-h-screen bg-void">
      {/* TODO(Amanda): placeholder hero — no video/poster asset yet. Once you have
          one, replace this gradient block with the same <video poster={...}>
          pattern used in Hero.tsx / Series.tsx (full-bleed, object-cover). */}
      <section className="relative flex min-h-[70vh] items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-ink via-void to-black" />
        <div className="absolute inset-0 bg-gradient-to-t from-void via-transparent to-void/40" />

        <div className="relative z-10 mx-auto flex max-w-2xl flex-col items-center px-6 text-center">
          <img src={crestIcon} alt="" className="mb-8 h-16 w-16 object-contain opacity-95" />
          <p className="eyebrow mb-4">House of Di Lorenzo</p>
          <h1 className="font-display text-4xl leading-[1.1] text-ivory sm:text-5xl md:text-6xl">
            Full-Length <span className="gold-text italic">Films</span>
          </h1>
          <p className="mt-5 max-w-xl font-body text-lg text-ivory-dim italic">
            The complete stories, start to end.
          </p>
        </div>
      </section>

      <div className="mx-auto mt-14 flex max-w-3xl flex-col gap-14 px-6 pb-16 sm:px-10">
        {films.length === 0 ? (
          <p className="reveal is-visible text-center font-body text-sm text-ivory-dim italic">
            Films coming soon.
          </p>
        ) : (
          films.map((film) => (
            <article key={film.id} className="reveal is-visible">
              <h2 className="mb-2 font-display text-2xl text-ivory sm:text-3xl">{film.title}</h2>
              <ViewCounter slug={`film-${film.id}`} className="mb-5" />
              <div className="relative aspect-video w-full overflow-hidden border border-ink-line bg-ink">
                <iframe
                  src={streamEmbedSrc(film.videoId)}
                  loading="lazy"
                  className="absolute inset-0 h-full w-full border-0"
                  allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                  allowFullScreen
                  title={film.title}
                />
              </div>

              {film.downloadPrice && (
                <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border border-ink-line bg-ink px-5 py-4">
                  <p className="font-body text-sm text-ivory-dim">
                    Stream it free above, or own the file — yours to keep, offline, no ads.
                  </p>
                  <a
                    href={film.downloadLink ?? '#'}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-gold shrink-0 whitespace-nowrap"
                  >
                    Download — {film.downloadPrice}
                  </a>
                </div>
              )}
            </article>
          ))
        )}

        <TipCallout />
      </div>

      <p className="mt-16 px-6 pb-16 text-center font-body text-xs tracking-wide text-ivory-dim/70 sm:px-10">
        <a href="/" className="text-gold underline underline-offset-4">
          Back to House of Di Lorenzo
        </a>
      </p>
    </div>
  )
}
