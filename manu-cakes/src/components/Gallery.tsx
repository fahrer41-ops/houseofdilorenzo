import roseWedding from '../assets/gallery-rose-wedding.jpg'
import chocolateBerry from '../assets/gallery-chocolate-berry.jpg'
import unicorn from '../assets/gallery-unicorn.jpg'
import nakedBlueberry from '../assets/gallery-naked-blueberry.jpg'
import heartDrip from '../assets/gallery-heart-drip.jpg'
import farm from '../assets/gallery-farm.jpg'
import { useLanguage } from '../i18n/LanguageContext'

const images = [roseWedding, chocolateBerry, unicorn, nakedBlueberry, heartDrip, farm]

export default function Gallery() {
  const { t } = useLanguage()

  return (
    <section id="gallery" className="bg-cream px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">{t.gallery.eyebrow}</p>
          <h2 className="font-display text-3xl text-plum sm:text-4xl">
            {t.gallery.titleStart} <span className="gold-text italic">{t.gallery.titleEmphasis}</span>
          </h2>
          <p className="mt-5 font-body text-plum-dim">{t.gallery.body}</p>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {t.gallery.pieces.map((title, i) => (
            <figure
              key={title}
              className="reveal group overflow-hidden rounded-2xl border border-blush-deep bg-blush"
            >
              <div className="aspect-square overflow-hidden">
                <img
                  src={images[i]}
                  alt={title}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
              </div>
              <figcaption className="px-5 py-4 font-display text-base italic text-plum">{title}</figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  )
}
