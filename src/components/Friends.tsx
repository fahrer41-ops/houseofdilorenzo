import SectionDivider from './SectionDivider'

type Film = {
  title: string
  filmmaker: string
  link: string
}

const films: Film[] = [
  {
    title: 'Rise of the Empire — The Siege',
    filmmaker: 'House of Di Lorenzo',
    link: 'https://higgsfield.ai/@houseofdilorenzo/projects/rise-of-an-empire-by-house-of-di-lorenzo',
  },
  {
    title: 'Amore Blu — The First Date',
    filmmaker: 'House of Di Lorenzo',
    link: 'https://higgsfield.ai/@houseofdilorenzo/projects/the-first-date',
  },
  {
    title: 'Moonlit Tail',
    filmmaker: 'Jeremy',
    link: 'https://higgsfield.ai/@jeremyw/projects/@id__37c6f33a-7685-4a11-adbd-d563b5bd5204',
  },
  {
    title: 'Journey',
    filmmaker: 'Scott',
    link: 'https://higgsfield.ai/@scott_s993/projects/journey',
  },
  {
    title: 'Glitch Day',
    filmmaker: 'Nash Koala',
    link: 'https://higgsfield.ai/@nash_koala_1064/projects/glitch-day',
  },
  {
    title: 'Fallen Leaves',
    filmmaker: 'Jacob Everett',
    link: 'https://higgsfield.ai/@jacob_everett/projects/fallen-leaves',
  },
  {
    title: 'Pon',
    filmmaker: 'Sam Candler',
    link: 'https://higgsfield.ai/@sam_candler/projects/pon',
  },
  {
    title: 'Ruby',
    filmmaker: 'Lucho',
    link: 'https://higgsfield.ai/@promptpicture/projects/ruby',
  },
]

function ExternalIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M7 17 17 7M9 7h8v8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export default function Friends() {
  return (
    <section id="friends" className="bg-void-deep px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">Free to Watch</p>
          <h2 className="font-display text-3xl text-ivory sm:text-4xl">
            Fellow <span className="gold-text italic">filmmakers</span>
          </h2>
          <p className="mt-5 font-body text-ivory-dim">
            Independent films from this year's festival — no subscription, no paywall. Great
            work deserves to be seen.
          </p>
        </div>

        <SectionDivider />

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {films.map((film) => (
            <a
              key={film.link}
              href={film.link}
              target="_blank"
              rel="noreferrer"
              className="reveal group flex items-center justify-between gap-4 border border-ink-line bg-ink px-6 py-5 transition-colors hover:border-gold"
            >
              <div>
                <p className="font-display text-lg text-ivory">{film.title}</p>
                <p className="mt-1 font-body text-sm text-ivory-dim">by {film.filmmaker}</p>
              </div>
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-gold-dim text-gold transition-colors group-hover:border-gold group-hover:text-gold-bright">
                <ExternalIcon />
              </span>
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}
