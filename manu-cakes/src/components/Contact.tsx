import { useLanguage } from '../i18n/LanguageContext'

function InstagramIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.2" cy="6.8" r="0.6" fill="currentColor" stroke="none" />
    </svg>
  )
}

export default function Contact() {
  const { t } = useLanguage()

  return (
    <section id="contact" className="bg-blush px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-2xl text-center">
        <p className="eyebrow reveal mb-4">{t.contact.eyebrow}</p>
        <h2 className="reveal font-display text-3xl text-plum sm:text-4xl">
          {t.contact.titleStart} <span className="gold-text italic">{t.contact.titleEmphasis}</span>
        </h2>
        <p className="reveal mt-5 font-body text-plum-dim">{t.contact.body}</p>
        <a
          href="https://instagram.com/manu.cakes78"
          target="_blank"
          rel="noreferrer"
          className="reveal btn-rose mt-9 inline-flex"
        >
          <InstagramIcon />
          @manu.cakes78
        </a>
      </div>
    </section>
  )
}
