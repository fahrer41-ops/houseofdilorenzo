import { useEffect } from 'react'
import posterImg from '../assets/voices-in-the-void-poster.jpg'
import ViewCounter from './ViewCounter'

const VIDEO_ID = 'acb73b13b559c997b2aad8f7ee891634'
// Cloudflare Stream — same account as the rest of the site's hosting.
const STREAM_CUSTOMER_CODE = 'ppcygtjv41676m0o'

function streamEmbedSrc(videoId: string) {
  const poster = encodeURIComponent(
    `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/thumbnails/thumbnail.jpg?time=&height=600`,
  )
  return `https://customer-${STREAM_CUSTOMER_CODE}.cloudflarestream.com/${videoId}/iframe?poster=${poster}`
}

export default function VoicesInTheVoid() {
  useEffect(() => {
    document.title = 'Voices in the Void: Hollow Heart — a film by man-aye'
  }, [])

  return (
    <div className="min-h-screen bg-[#07080b] font-body text-[#ece6d9]">
      <section className="relative flex min-h-[85vh] items-end overflow-hidden">
        <div className="absolute inset-0">
          <img
            src={posterImg}
            alt=""
            className="h-full w-full object-cover object-[center_30%]"
          />
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
            A film by <span className="text-[#ece6d9]">man-aye</span>{' '}
            <span className="text-[#6e6657]">(Cameron)</span>
          </p>
        </div>
      </section>

      <section className="px-6 py-16 sm:px-10">
        <div className="mx-auto max-w-4xl">
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

          <div className="mt-6 text-center">
            <a
              href="https://higgsfield.ai/@man-aye/projects/voices-in-the-void"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-blood px-9 py-3.5 font-body text-sm font-semibold tracking-[0.14em] text-[#f2ede0] uppercase transition-colors hover:bg-blood-bright"
            >
              Vote for this Film
            </a>
          </div>

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
