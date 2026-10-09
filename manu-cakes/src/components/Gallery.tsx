import roseWedding from '../assets/gallery-rose-wedding.jpg'
import nakedBlueberry from '../assets/gallery-naked-blueberry.jpg'
import heartDrip from '../assets/gallery-heart-drip.jpg'
import farm from '../assets/gallery-farm.jpg'
import birthdayPinkGold from '../assets/birthday-pink-gold.jpg'
import teddyBearFirst from '../assets/teddy-bear-first.jpg'
import ohBaby from '../assets/oh-baby.jpg'
import moonStars from '../assets/moon-stars.jpg'
import chocolateFig from '../assets/chocolate-fig.jpg'
import eighteenDennis from '../assets/eighteen-dennis.jpg'
import christeningThomas from '../assets/christening-thomas.jpg'
import pistachio50 from '../assets/pistachio-50.jpg'
import { useLanguage } from '../i18n/LanguageContext'

const images = [
  roseWedding,
  heartDrip,
  farm,
  nakedBlueberry,
  birthdayPinkGold,
  teddyBearFirst,
  ohBaby,
  moonStars,
  chocolateFig,
  eighteenDennis,
  christeningThomas,
  pistachio50,
]

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
              className="reveal group overflow-hidden rounded-2xl border border-gold/30 bg-blush shadow-sm shadow-plum/5"
            >
              <div className="aspect-[4/5] overflow-hidden">
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
