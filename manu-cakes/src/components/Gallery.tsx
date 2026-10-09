import roseWedding from '../assets/gallery-rose-wedding.jpg'
import chocolateBerry from '../assets/gallery-chocolate-berry.jpg'
import unicorn from '../assets/gallery-unicorn.jpg'
import nakedBlueberry from '../assets/gallery-naked-blueberry.jpg'
import heartDrip from '../assets/gallery-heart-drip.jpg'
import farm from '../assets/gallery-farm.jpg'

const pieces = [
  { image: roseWedding, title: 'Torta Nuziale, Rose Rosse' },
  { image: chocolateBerry, title: 'Torta al Cioccolato e Frutti di Bosco' },
  { image: unicorn, title: 'Torta Unicorno' },
  { image: nakedBlueberry, title: 'Naked Cake, Mirtilli e Fiori' },
  { image: heartDrip, title: '"Auguri Amore"' },
  { image: farm, title: 'Torta a Tema Fattoria' },
]

export default function Gallery() {
  return (
    <section id="gallery" className="bg-cream px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">Creazioni</p>
          <h2 className="font-display text-3xl text-plum sm:text-4xl">
            Ogni torta, <span className="gold-text italic">una storia</span>
          </h2>
          <p className="mt-5 font-body text-plum-dim">
            Una selezione delle creazioni di Manuela — ogni pezzo fatto a mano, su misura per il
            momento che festeggi.
          </p>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {pieces.map((piece) => (
            <figure
              key={piece.title}
              className="reveal group overflow-hidden rounded-2xl border border-blush-deep bg-blush"
            >
              <div className="aspect-square overflow-hidden">
                <img
                  src={piece.image}
                  alt={piece.title}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
              </div>
              <figcaption className="px-5 py-4 font-display text-base italic text-plum">
                {piece.title}
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  )
}
