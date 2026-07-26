import { useEffect, useState } from 'react'
import crestIcon from '../assets/crest-icon.png'

const LINKS = [
  { href: '#work', label: 'The Work' },
  { href: '#services', label: 'What I Create' },
  { href: '#pricing', label: 'Investment' },
  { href: '#about', label: 'About' },
  { href: '#contact', label: 'Contact' },
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
        scrolled ? 'bg-void/90 backdrop-blur-sm border-b border-ink-line' : 'bg-transparent'
      }`}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-10">
        <a href="#top" className="flex items-center gap-3 text-ivory">
          <img src={crestIcon} alt="" className="h-9 w-9 shrink-0 object-contain" />
          <span className="font-display text-lg tracking-[0.15em]">DI LORENZO</span>
        </a>

        <nav className="hidden items-center gap-9 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm tracking-[0.12em] text-ivory-dim uppercase transition-colors hover:text-gold-bright"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <button
          type="button"
          onClick={() => setMenuOpen((v) => !v)}
          className="flex h-9 w-9 flex-col items-center justify-center gap-1.5 md:hidden"
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
        >
          <span className={`h-px w-6 bg-gold transition-transform ${menuOpen ? 'translate-y-2 rotate-45' : ''}`} />
          <span className={`h-px w-6 bg-gold transition-opacity ${menuOpen ? 'opacity-0' : ''}`} />
          <span className={`h-px w-6 bg-gold transition-transform ${menuOpen ? '-translate-y-2 -rotate-45' : ''}`} />
        </button>
      </div>

      {menuOpen && (
        <nav className="flex flex-col gap-1 border-t border-ink-line bg-void px-6 py-4 md:hidden">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className="py-2.5 text-sm tracking-[0.12em] text-ivory-dim uppercase"
            >
              {link.label}
            </a>
          ))}
        </nav>
      )}
    </header>
  )
}
