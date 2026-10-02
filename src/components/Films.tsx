import { useEffect } from 'react'
import crestIcon from '../assets/crest-icon.png'
import TipCallout from './TipCallout'

// TODO(Amanda): tell me what goes here — your completed full-length
// films (Rise of an Empire: The Siege, Amore Blu...), separate from
// the homepage Portfolio clips and the episodic Series. Embedded here,
// or linked out to YouTube?
type Film = {
  id: string
  title: string
  description?: string
  link: string
}

const films: Film[] = []

export default function Films() {
  useEffect(() => {
    document.title = 'Films — House of Di Lorenzo'
  }, [])

  return (
    <div className="min-h-screen bg-void px-6 py-16 sm:px-10">
      <div className="mx-auto max-w-2xl text-center">
        <img src={crestIcon} alt="" className="mx-auto mb-8 h-16 w-16 object-contain opacity-95" />
        <p className="eyebrow mb-4">House of Di Lorenzo</p>
        <h1 className="font-display text-4xl text-ivory sm:text-5xl">
          Full-Length <span className="gold-text italic">Films</span>
        </h1>
        <p className="mt-5 font-body text-ivory-dim">The complete stories, start to end.</p>
      </div>

      <div className="mx-auto mt-14 flex max-w-3xl flex-col gap-10">
        {films.length === 0 ? (
          <p className="reveal is-visible text-center font-body text-sm text-ivory-dim italic">
            Films coming soon.
          </p>
        ) : (
          films.map((film) => (
            <a
              key={film.id}
              href={film.link}
              target="_blank"
              rel="noreferrer"
              className="group flex items-center justify-between border border-ink-line bg-ink px-6 py-5 transition-colors hover:border-gold"
            >
              <div className="text-left">
                <p className="font-display text-lg text-ivory">{film.title}</p>
                {film.description && (
                  <p className="mt-1 font-body text-sm text-ivory-dim">{film.description}</p>
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

        <TipCallout />
      </div>

      <p className="mt-16 text-center font-body text-xs tracking-wide text-ivory-dim/70">
        <a href="/" className="text-gold underline underline-offset-4">
          Back to House of Di Lorenzo
        </a>
      </p>
    </div>
  )
}
