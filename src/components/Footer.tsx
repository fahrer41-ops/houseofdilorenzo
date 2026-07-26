import Monogram from './Monogram'

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
        <p className="font-body text-xs tracking-wide text-ivory-dim/70">
          &copy; {new Date().getFullYear()} House of Di Lorenzo Productions. All rights
          reserved.
        </p>
      </div>
    </footer>
  )
}
