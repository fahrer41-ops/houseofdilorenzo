import { useEffect } from 'react'
import crestIcon from '../assets/crest-icon.png'

type Film = {
  title: string
  filmmaker?: string
  link: string
}

// TODO(Amanda): send me each friend's film — title, filmmaker name (optional), and watch link.
const films: Film[] = []

export default function FreeMovies() {
  useEffect(() => {
    document.title = 'Free Movies — House of Di Lorenzo'
  }, [])

  return (
    <div className="min-h-screen bg-void px-6 py-16 sm:px-10">
      <div className="mx-auto max-w-2xl text-center">
        <img src={crestIcon} alt="" className="mx-auto mb-8 h-16 w-16 object-contain opacity-95" />
        <p className="eyebrow mb-4">No Catch. No Paywall.</p>
        <h1 className="font-display text-4xl text-ivory sm:text-5xl">
          Free <span className="gold-text italic">Movies</span>
        </h1>
        <p className="mt-5 font-body text-ivory-dim">
          No subscription needed. Independent films from festival filmmakers, free to watch —
          because great work deserves to be seen.
        </p>
      </div>

      <div className="mx-auto mt-14 grid max-w-3xl gap-4">
        {films.length === 0 ? (
          <p className="reveal is-visible text-center font-body text-sm text-ivory-dim italic">
            Films coming soon.
          </p>
        ) : (
          films.map((film) => (
            <a
              key={film.link}
              href={film.link}
              target="_blank"
              rel="noreferrer"
              className="group flex items-center justify-between border border-ink-line bg-ink px-6 py-5 transition-colors hover:border-gold"
            >
              <div className="text-left">
                <p className="font-display text-lg text-ivory">{film.title}</p>
                {film.filmmaker && (
                  <p className="mt-1 font-body text-sm text-ivory-dim">by {film.filmmaker}</p>
                )}
              </div>
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-gold-dim text-gold transition-colors group-hover:border-gold group-hover:text-gold-bright">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z" />
                </svg>
              </span>
            </a>
          ))
        )}
      </div>

      <p className="mt-16 text-center font-body text-xs tracking-wide text-ivory-dim/70">
        Curated by{' '}
        <a href="https://houseofdilorenzo.com" className="text-gold underline underline-offset-4">
          House of Di Lorenzo
        </a>
      </p>
    </div>
  )
}
