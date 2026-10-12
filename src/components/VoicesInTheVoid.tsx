import { useEffect, useRef, useState } from 'react'
import posterImg from '../assets/voices-in-the-void-poster.jpg'
import ViewCounter from './ViewCounter'

const VIDEO_ID = 'acb73b13b559c997b2aad8f7ee891634'
const HIGGSFIELD_URL = 'https://higgsfield.ai/@man-aye/projects/voices-in-the-void'
// Cloudflare Stream — same account as the rest of the site's hosting.
const STREAM_CUSTOMER_CODE = 'ppcygtjv41676m0o'

function streamEmbedSrc(videoId: string) {
  const poster = encodeURIComponent(
    `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/thumbnails/thumbnail.jpg?time=&height=600`,
  )
  return `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/iframe?poster=${poster}`
}

type Intent = 'vote' | 'watch' | null

export default function VoicesInTheVoid() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [intent, setIntent] = useState<Intent>(null)

  useEffect(() => {
    document.title = 'Voices in the Void: Hollow Heart — a film by man-aye'
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
    <div className="min-h-screen bg-[#07080b] font-body text-[#ece6d9]">
      <section className="relative flex min-h-[85vh] items-end overflow-hidden">
        <div className="absolute inset-0">
          <video
            ref={videoRef}
            poster={posterImg}
            muted
            loop
            playsInline
            preload="auto"
            className="h-full w-full object-cover object-[center_30%]"
          >
            <source src="/voices-banner.webm" type="video/webm" />
            <source src="/voices-banner.mp4" type="video/mp4" />
          </video>
          <div className="absolute inset-0 bg-gradient-to-b from-[#07080b]/20 via-[#07080b]/55 to-[#07080b]" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#07080b] via-transparent to-transparent" />
        </div>

        <div className="relative z-10 mx-auto w-full max-w-4xl px-6 pb-16 sm:px-10">
          <p className="mb-3 font-body text-xs tracking-[0.3em] text-blood-bright uppercase">
            A Guest Film — Hosted by House of Di Lorenzo
          </p>
          <h1
            className="font-display text-5xl leading-[1.05] text-[#f2ede0] sm:text-6xl md:text-7xl"
            style={{ textShadow: '0 4px 24px rgba(0,0,0,0.6)' }}
          >
            Voices in the Void
          </h1>
          <p className="mt-1 font-display text-2xl italic text-blood-bright sm:text-3xl">Hollow Heart</p>
          <p className="mt-6 max-w-xl font-body text-[15px] leading-relaxed text-[#cfc7b8]">
            Souls lost to trauma, depression, grief, and anger awaken hollowed out in a mental hell. One
            Hollow Heart must find a way to free them.
          </p>
          <p className="mt-6 font-body text-sm tracking-[0.1em] text-[#9b9183] uppercase">
            A film by <span className="text-[#ece6d9]">man-aye</span>
          </p>
        </div>
      </section>

      <section className="px-6 py-16 sm:px-10">
        <div className="mx-auto max-w-4xl">
          {intent === null && (
            <div className="border border-[#2a2420] bg-black/40 px-6 py-14 text-center sm:px-10">
              <p className="font-display text-2xl text-[#f2ede0] sm:text-3xl">What brings you here?</p>
              <p className="mx-auto mt-3 max-w-md font-body text-sm text-[#9b9183]">
                Voting for this film only counts when it happens on Higgsfield itself — so pick the red
                door and you won't need to watch it twice.
              </p>
              <div className="mt-9 flex flex-col items-center justify-center gap-4 sm:flex-row">
                <a
                  href={HIGGSFIELD_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setIntent('vote')}
                  className="inline-flex w-full flex-col items-center border border-blood-bright bg-blood px-9 py-4 transition-colors hover:bg-blood-bright sm:w-auto"
                >
                  <span className="font-body text-sm font-semibold tracking-[0.14em] text-[#f2ede0] uppercase">
                    Voting
                  </span>
                  <span className="mt-1 font-body text-xs text-[#f2ede0]/70">Watch &amp; vote on Higgsfield</span>
                </a>
                <button
                  type="button"
                  onClick={() => setIntent('watch')}
                  className="inline-flex w-full flex-col items-center border border-[#3a332c] px-9 py-4 transition-colors hover:border-blood-bright sm:w-auto"
                >
                  <span className="font-body text-sm font-semibold tracking-[0.14em] text-[#ece6d9] uppercase">
                    Watching
                  </span>
                  <span className="mt-1 font-body text-xs text-[#9b9183]">Just here to see the film</span>
                </button>
              </div>
            </div>
          )}

          {intent === 'vote' && (
            <div className="border border-blood-bright/60 bg-black/40 px-6 py-14 text-center sm:px-10">
              <p className="font-display text-2xl text-[#f2ede0] sm:text-3xl">Opening Higgsfield…</p>
              <p className="mx-auto mt-3 max-w-md font-body text-sm text-[#9b9183]">
                A new tab should have opened. Watch the film there and the vote button unlocks right after —
                no need to watch it again here.
              </p>
              <a
                href={HIGGSFIELD_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-7 inline-block bg-blood px-9 py-3.5 font-body text-sm font-semibold tracking-[0.14em] text-[#f2ede0] uppercase transition-colors hover:bg-blood-bright"
              >
                Didn't open? Click here
              </a>
              <p className="mt-6">
                <button
                  type="button"
                  onClick={() => setIntent('watch')}
                  className="font-body text-xs tracking-[0.1em] text-[#9b9183] underline underline-offset-4 hover:text-blood-bright"
                >
                  Or just watch it here instead
                </button>
              </p>
            </div>
          )}

          {intent === 'watch' && (
            <>
              <ViewCounter slug="voices-in-the-void" className="mb-5" />
              <div className="relative aspect-video w-full overflow-hidden border border-[#2a2420] bg-black shadow-[0_0_60px_-15px_rgba(138,31,31,0.35)]">
                <iframe
                  src={streamEmbedSrc(VIDEO_ID)}
                  loading="lazy"
                  className="absolute inset-0 h-full w-full border-0"
                  allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
                  allowFullScreen
                  title="Voices in the Void: Hollow Heart"
                />
              </div>

              <p className="mt-6 text-center font-body text-xs text-[#9b9183]">
                Want to vote too? Your watch here won't count there —{' '}
                <a
                  href={HIGGSFIELD_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blood-bright underline underline-offset-4"
                >
                  watch once on Higgsfield to vote
                </a>
                .
              </p>
            </>
          )}

          <div className="mt-10 border-t border-[#201c18] pt-8 text-center">
            <p className="font-body text-sm text-[#9b9183]">
              Entered in the{' '}
              <span className="text-[#ece6d9]">Higgsfield Global Film Festival</span> — if you enjoyed it,
              consider supporting man-aye's work.
            </p>
            <a
              href="https://instagram.com/man_aye"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-5 inline-block border border-blood-bright/70 px-7 py-3 font-body text-xs tracking-[0.14em] text-blood-bright uppercase transition-colors hover:border-blood-bright hover:bg-blood-dim/30"
            >
              Follow man-aye on Instagram
            </a>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#201c18] px-6 py-10 text-center">
        <a href="/" className="font-body text-sm text-blood-bright underline underline-offset-4">
          Back to House of Di Lorenzo
        </a>
      </footer>
    </div>
  )
}
