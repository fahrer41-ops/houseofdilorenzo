import { useEffect, useRef } from 'react'

const heroPoster = '/hero-video-poster.jpg'

export default function Hero() {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!prefersReducedMotion) {
      videoRef.current?.play().catch(() => {
        // Autoplay can be blocked by the browser; the poster frame stands in fine.
      })
    }
  }, [])

  return (
    <section
      id="top"
      className="relative flex min-h-screen items-center overflow-hidden"
    >
      <div className="absolute inset-0">
        <video
          ref={videoRef}
          poster={heroPoster}
          muted
          loop
          playsInline
          preload="auto"
          className="h-full w-full object-cover object-center"
        >
          <source src="/hero-video.webm" type="video/webm" />
          <source src="/hero-video.mp4" type="video/mp4" />
        </video>
        <div
          className="absolute inset-0"
          style={{
            background:
              'radial-gradient(120% 120% at 15% 20%, rgba(255,154,77,0.35) 0%, rgba(196,19,44,0.45) 45%, rgba(11,9,8,0.75) 85%)',
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-void via-void/10 to-transparent" />
      </div>

      <div className="relative z-10 mx-auto w-full max-w-6xl px-6 py-32 sm:px-10">
        <p
          className="eyebrow reveal is-visible mb-6"
          style={{ color: 'var(--color-ivory)' }}
        >
          William James Creative
        </p>

        <h1 className="font-display leading-[0.9] font-black text-ivory drop-shadow-[0_2px_20px_rgba(0,0,0,0.35)]">
          <span className="block text-6xl sm:text-7xl md:text-8xl">CREATIVE</span>
          <span className="mt-2 block text-right text-6xl italic sm:text-7xl md:text-8xl">
            WORK.
          </span>
        </h1>

        {/* TODO(Amanda): swap once Will sends his own words on this — pulled
            from his Behance bio in the meantime. */}
        <p className="reveal is-visible mt-8 max-w-md font-body text-lg text-ivory">
          AI-directed music videos, character art and film — built frame by frame.
        </p>

        <div className="reveal is-visible mt-10 flex flex-col gap-4 sm:flex-row">
          <a href="#work" className="btn-ember">
            View Work
          </a>
          <a href="#contact" className="btn-ghost">
            Get in Touch
          </a>
        </div>
      </div>
    </section>
  )
}
