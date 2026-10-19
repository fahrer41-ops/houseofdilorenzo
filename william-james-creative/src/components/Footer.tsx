export default function Footer() {
  return (
    <footer className="border-t border-ink-line bg-void px-6 py-10 text-center sm:px-10">
      <p className="font-display text-lg font-black text-ivory">
        William <span className="ember-text">James</span>
      </p>
      <p className="mt-2 font-body text-xs tracking-wide text-ivory-dim/70">
        &copy; {new Date().getFullYear()} William James Creative ·{' '}
        <a
          href="https://www.instagram.com/williamjamesb166er"
          target="_blank"
          rel="noopener noreferrer"
          className="text-ember-bright hover:text-ember"
        >
          @williamjamesb166er
        </a>
      </p>
    </footer>
  )
}
