import { useLanguage } from '../i18n/LanguageContext'

export default function About() {
  const { t } = useLanguage()

  return (
    <section id="about" className="bg-blush px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-3xl text-center">
        <p className="eyebrow reveal mb-4">{t.about.eyebrow}</p>
        <h2 className="reveal font-display text-3xl text-plum sm:text-4xl">
          {t.about.titleStart} <span className="gold-text italic">{t.about.titleEmphasis}</span>
          {t.about.titleEnd}
        </h2>
        <p className="reveal mt-7 font-body text-lg leading-relaxed text-plum-dim">{t.about.body}</p>
        <p className="reveal mt-5 font-display text-xl italic text-rose">{t.about.quote}</p>
      </div>
    </section>
  )
}
