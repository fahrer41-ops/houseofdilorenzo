import Monogram from './Monogram'

const INSTAGRAM_LINKS = [
  { handle: '@thehouseofdilorenzo', url: 'https://instagram.com/thehouseofdilorenzo' },
  { handle: '@amanda.dilorenzo', url: 'https://instagram.com/amanda.dilorenzo' },
]

function InstagramIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="12" cy="12" r="4.2" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" />
    </svg>
  )
}

export default function Footer() {
  return (
    <footer className="border-t border-ink-line bg-void-deep px-6 py-12 sm:px-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-6 text-center sm:flex-row sm:justify-between sm:text-left">
        <div className="flex items-center gap-3">
          <Monogram className="h-8 w-8 opacity-80" />
          <span className="font-display text-sm tracking-[0.15em] text-ivory-dim">
            HOUSE OF DI LORENZO
          </span>
        </div>

        <div className="flex items-center gap-5">
          {INSTAGRAM_LINKS.map((link) => (
            <a
              key={link.handle}
              href={link.url}
              target="_blank"
              rel="noreferrer"
              aria-label={`Instagram — ${link.handle}`}
              className="flex items-center gap-2 text-ivory-dim transition-colors hover:text-gold-bright"
            >
              <InstagramIcon />
              <span className="font-body text-xs tracking-wide">{link.handle}</span>
            </a>
          ))}
        </div>

        <p className="font-body text-xs tracking-wide text-ivory-dim/70">
          &copy; {new Date().getFullYear()} House of Di Lorenzo Productions. All rights
          reserved.
        </p>
      </div>
    </footer>
  )
}
