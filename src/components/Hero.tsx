import heroImage from '../assets/rise-of-empire-2.jpg'
import Monogram from './Monogram'

export default function Hero() {
  return (
    <section id="top" className="relative flex min-h-screen items-center justify-center overflow-hidden">
      <div className="absolute inset-0">
        <img
          src={heroImage}
          alt=""
          className="h-full w-full object-cover object-center [animation:hero-drift_28s_ease-in-out_infinite_alternate]"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-void/80 via-void/55 to-void" />
        <div className="absolute inset-0 bg-void/25" />
      </div>

      <div className="relative z-10 mx-auto flex max-w-3xl flex-col items-center px-6 text-center">
        <Monogram className="mb-8 h-16 w-16 opacity-90" />
        <p className="eyebrow mb-6">House of Di Lorenzo Productions</p>
        <h1 className="font-display text-4xl leading-[1.1] text-ivory sm:text-5xl md:text-6xl">
          Art is the language <span className="gold-text italic">of the soul</span>
        </h1>
        <p className="mt-6 max-w-xl font-body text-lg text-ivory-dim italic">
          Cinematic AI video production — character-consistent storytelling, built frame by
          frame.
        </p>

        <div className="mt-10 flex flex-col gap-4 sm:flex-row">
          <a href="#work" className="btn-gold">
            View Portfolio
          </a>
          <a href="#contact" className="btn-ghost">
            Get a Quote
          </a>
        </div>
      </div>

      <a
        href="#work"
        aria-label="Scroll to portfolio"
        className="absolute bottom-8 left-1/2 z-10 hidden -translate-x-1/2 flex-col items-center gap-2 text-gold-dim transition-colors hover:text-gold sm:flex"
      >
        <span className="h-12 w-px bg-current" />
      </a>
    </section>
  )
}
