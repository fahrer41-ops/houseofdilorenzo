import { useEffect, useState } from 'react'
import { useLanguage } from '../i18n/LanguageContext'
import LanguageToggle from './LanguageToggle'

export default function Header() {
  const { t } = useLanguage()
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
        scrolled ? 'border-b border-blush-deep bg-cream/90 backdrop-blur-sm' : 'bg-transparent'
      }`}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 sm:px-10">
        <a href="/" className="font-display text-xl italic tracking-wide text-plum">
          Manu <span className="gold-text not-italic">Cakes</span>
        </a>

        <nav className="hidden items-center gap-8 md:flex">
          {t.header.nav.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm tracking-[0.08em] text-plum-dim uppercase transition-colors hover:text-rose"
            >
              {link.label}
            </a>
          ))}
          <LanguageToggle />
          <a href="https://instagram.com/manu.cakes78" target="_blank" rel="noreferrer" className="btn-rose">
            {t.header.cta}
          </a>
        </nav>

        <div className="flex items-center gap-4 md:hidden">
          <LanguageToggle />
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            className="flex h-9 w-9 flex-col items-center justify-center gap-1.5"
            aria-label="Menu"
            aria-expanded={menuOpen}
          >
            <span className={`h-px w-6 bg-rose transition-transform ${menuOpen ? 'translate-y-2 rotate-45' : ''}`} />
            <span className={`h-px w-6 bg-rose transition-opacity ${menuOpen ? 'opacity-0' : ''}`} />
            <span
              className={`h-px w-6 bg-rose transition-transform ${menuOpen ? '-translate-y-2 -rotate-45' : ''}`}
            />
          </button>
        </div>
      </div>

      {menuOpen && (
        <nav className="flex flex-col gap-1 border-t border-blush-deep bg-cream px-6 py-4 md:hidden">
          {t.header.nav.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
              className="py-2.5 text-sm tracking-[0.08em] text-plum-dim uppercase"
            >
              {link.label}
            </a>
          ))}
          <a
            href="https://instagram.com/manu.cakes78"
            target="_blank"
            rel="noreferrer"
            onClick={() => setMenuOpen(false)}
            className="btn-rose mt-2 justify-center"
          >
            {t.header.cta}
          </a>
        </nav>
      )}
    </header>
  )
}
