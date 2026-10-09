import heroCake from '../assets/hero-heart-cake.jpg'
import { useLanguage } from '../i18n/LanguageContext'

export default function Hero() {
  const { t } = useLanguage()

  return (
    <section id="top" className="relative flex min-h-screen items-center overflow-hidden bg-blush pt-24">
      <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 sm:px-10 lg:grid-cols-2">
        <div className="reveal is-visible text-center lg:text-left">
          <p className="eyebrow mb-5">{t.hero.eyebrow}</p>
          <h1 className="font-display text-4xl leading-[1.12] text-plum sm:text-5xl md:text-6xl">
            {t.hero.titleStart} <span className="gold-text italic">{t.hero.titleEmphasis}</span>{' '}
            {t.hero.titleEnd}
          </h1>
          <p className="mx-auto mt-6 max-w-md font-body text-lg text-plum-dim lg:mx-0">{t.hero.body}</p>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center lg:justify-start">
            <a href="https://instagram.com/manu.cakes78" target="_blank" rel="noreferrer" className="btn-rose">
              {t.hero.ctaPrimary}
            </a>
            <a href="#gallery" className="btn-ghost">
              {t.hero.ctaSecondary}
            </a>
          </div>
        </div>

        <div className="reveal is-visible relative">
          <div className="absolute -inset-4 -z-10 rounded-[2.5rem] bg-dusk/70 sm:-inset-6" />
          <div className="overflow-hidden rounded-[2rem] border-2 border-gold/40 shadow-xl shadow-plum/20">
            <img src={heroCake} alt={t.hero.heroImageAlt} className="w-full object-cover" />
          </div>
        </div>
      </div>
    </section>
  )
}
