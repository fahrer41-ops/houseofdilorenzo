import { useEffect } from 'react'
import filmsHeroPoster from '../assets/films-hero-poster.png'
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
      {/* TODO(Amanda): placeholder hero — this is the studio credits card, used
          as a stand-in until the real hero video exists. Once you have one,
          swap this <img> for the <video poster={...}> pattern used in
          Hero.tsx / Series.tsx (full-bleed, object-cover). Kept as
          object-contain here since this image is a wide banner graphic, not
          footage meant to be cropped. */}
      <section className="relative flex min-h-[55vh] items-center justify-center overflow-hidden bg-black">
        <img
          src={filmsHeroPoster}
          alt="House of Di Lorenzo — directed, created and produced by Amanda Fahrer"
          className="h-full w-full object-contain"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-void via-transparent to-transparent" />
      </section>

      <div className="mx-auto max-w-2xl px-6 pt-14 text-center sm:px-10">
        <h1 className="font-display text-4xl leading-[1.1] text-ivory sm:text-5xl md:text-6xl">
          Full-Length <span className="gold-text italic">Films</span>
        </h1>
        <p className="mt-5 font-body text-lg text-ivory-dim italic">The complete stories, start to end.</p>
      </div>

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
