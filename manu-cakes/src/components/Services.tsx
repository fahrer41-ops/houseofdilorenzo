import { useLanguage } from '../i18n/LanguageContext'

export default function Services() {
  const { t } = useLanguage()

  return (
    <section id="services" className="bg-cream px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">{t.services.eyebrow}</p>
          <h2 className="font-display text-3xl text-plum sm:text-4xl">
            {t.services.titleStart} <span className="gold-text italic">{t.services.titleEmphasis}</span>
          </h2>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {t.services.items.map((service) => {
            const cardClass =
              'reveal border px-7 py-8 transition-colors ' +
              ('link' in service
                ? 'border-gold bg-blush-deep hover:border-rose'
                : 'border-blush-deep bg-blush hover:border-rose')

            const inner = (
              <>
                <h3 className="font-display text-xl text-plum">{service.title}</h3>
                <p className="mt-3 font-body text-sm leading-relaxed text-plum-dim">{service.description}</p>
              </>
            )

            return 'link' in service ? (
              <a key={service.title} href={service.link} className={cardClass}>
                {inner}
              </a>
            ) : (
              <div key={service.title} className={cardClass}>
                {inner}
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
