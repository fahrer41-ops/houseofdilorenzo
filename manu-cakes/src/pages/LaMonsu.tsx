import { useEffect } from 'react'
import laMonsuHero from '../assets/la-monsu-hero.jpg'
import { useLanguage } from '../i18n/LanguageContext'
import LanguageToggle from '../components/LanguageToggle'
import useReveal from '../hooks/useReveal'

export default function LaMonsu() {
  const { t } = useLanguage()
  useReveal()

  useEffect(() => {
    document.title = 'La Monsù Napoletana — Manu Cakes'
  }, [])

  return (
    <div className="min-h-screen bg-cream">
      <header className="flex items-center justify-between px-6 py-5 sm:px-10">
        <a href="/" className="text-sm tracking-[0.08em] text-plum-dim uppercase hover:text-rose">
          &larr; {t.laMonsu.backLink}
        </a>
        <LanguageToggle />
      </header>

      <section className="px-6 pb-20 sm:px-10">
        <div className="mx-auto max-w-3xl text-center">
          <div className="reveal is-visible mx-auto mb-10 max-w-md overflow-hidden rounded-[2rem] border border-blush-deep shadow-xl shadow-rose/10">
            <img src={laMonsuHero} alt="La Monsù Napoletana" className="w-full object-cover" />
          </div>

          <p className="eyebrow reveal is-visible mb-4">{t.laMonsu.eyebrow}</p>
          <h1 className="reveal is-visible font-display text-3xl text-plum sm:text-5xl">{t.laMonsu.title}</h1>
          <p className="reveal is-visible mx-auto mt-6 max-w-xl font-body text-lg text-plum-dim">
            {t.laMonsu.body}
          </p>

          <a
            href="https://instagram.com/manu.cakes78"
            target="_blank"
            rel="noreferrer"
            className="reveal is-visible btn-rose mt-9 inline-flex"
          >
            {t.laMonsu.cta}
          </a>
        </div>

        <div className="mx-auto mt-24 max-w-4xl">
          <h2 className="reveal text-center font-display text-2xl text-plum sm:text-3xl">
            {t.laMonsu.stepsTitle}
          </h2>
          <div className="mt-10 grid gap-5 sm:grid-cols-3">
            {t.laMonsu.steps.map((step, i) => (
              <div key={step.title} className="reveal border border-blush-deep bg-blush px-6 py-7 text-center">
                <p className="font-display text-3xl text-gold">{i + 1}</p>
                <h3 className="mt-2 font-display text-lg text-plum">{step.title}</h3>
                <p className="mt-2 font-body text-sm leading-relaxed text-plum-dim">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-blush-deep px-6 py-10 text-center sm:px-10">
        <p className="font-display text-lg italic text-plum">
          Manu <span className="gold-text not-italic">Cakes</span>
        </p>
        <p className="mt-2 font-body text-xs tracking-wide text-plum-dim/70">{t.footer.location}</p>
      </footer>
    </div>
  )
}
