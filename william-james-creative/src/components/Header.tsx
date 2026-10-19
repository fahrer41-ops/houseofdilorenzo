import { useEffect, useState } from 'react'

const NAV_LINKS = [
  { href: '#work', label: 'Work' },
  { href: '#about', label: 'About' },
  { href: '#services', label: 'Services' },
]

export default function Header() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-colors duration-500 ${
        scrolled ? 'border-b border-ink-line bg-void/90 backdrop-blur-sm' : 'bg-transparent'
      }`}
    >
      <div
        className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-10"
        style={{ textShadow: scrolled ? 'none' : '0 1px 10px rgba(0,0,0,0.45)' }}
      >
        <a href="/" className="font-display text-xl font-extrabold tracking-tight text-ivory">
          William <span className="ember-text">James</span>
        </a>

        <nav className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm tracking-[0.06em] text-ivory uppercase transition-colors hover:text-ember-bright"
            >
              {link.label}
            </a>
          ))}
          <a href="#contact" className="btn-ember">
            Let's Talk
          </a>
        </nav>

        <button
          type="button"
          onClick={() => setMenuOpen((v) => !v)}
          className="flex h-9 w-9 flex-col items-center justify-center gap-1.5 md:hidden"
          aria-label="Menu"
          aria-expanded={menuOpen}
        >
          <span className={`h-px w-6 bg-ivory transition-transform ${menuOpen ? 'translate-y-2 rotate-45' : ''}`} />
          <span className={`h-px w-6 bg-ivory transition-opacity ${menuOpen ? 'opacity-0' : ''}`} />
          <span
            className={`h-px w-6 bg-ivory transition-transform ${menuOpen ? '-translate-y-2 -rotate-45' : ''}`}
          />
        </button>
      </div>

      {menuOpen && (
        <nav className="flex flex-col gap-1 border-t border-ink-line bg-void px-6 py-4 md:hidden">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className="py-2.5 text-sm tracking-[0.06em] text-ivory-dim uppercase"
            >
              {link.label}
            </a>
          ))}
          <a href="#contact" onClick={() => setMenuOpen(false)} className="btn-ember mt-2 justify-center">
            Let's Talk
          </a>
        </nav>
      )}
    </header>
  )
}
