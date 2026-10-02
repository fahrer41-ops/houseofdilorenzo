import { useEffect } from 'react'
import crestIcon from '../assets/crest-icon.png'
import recordsDistributionPoster from '../assets/shop/records-distribution-poster.jpg'
import posterAlaric from '../assets/shop/posters/poster-alaric-king.jpg'
import posterLisandraValkyrie from '../assets/shop/posters/poster-lisandra-valkyrie.jpg'
import posterOdin from '../assets/shop/posters/poster-odin-allfather.jpg'
import posterDante from '../assets/shop/posters/poster-dante.jpg'
import posterRunar from '../assets/shop/posters/poster-runar.jpg'
import posterBjorn from '../assets/shop/posters/poster-bjorn.jpg'

type Product = {
  id: string
  name: string
  price: string
  description?: string
  image: string
  buyLink: string
}

const products: Product[] = [
  {
    id: 'music-distribution',
    name: 'Music Distribution — House of Di Lorenzo Records',
    // TODO(Amanda): confirm this is the real price, not just the template placeholder.
    price: '$15',
    description:
      'Get your track on 26 worldwide platforms — iTunes, Spotify, YouTube Music, TikTok & more. One-time flat fee, you keep 100% of your streaming royalties.',
    image: recordsDistributionPoster,
    buyLink: 'https://ko-fi.com/c/81e1e85333',
  },
  {
    id: 'poster-alaric',
    name: 'Alaric — King of Di Lorenzo',
    price: '$4',
    description: 'Digital poster, full resolution.',
    image: posterAlaric,
    buyLink: 'https://ko-fi.com/s/4aebbe1a5b',
  },
  {
    id: 'poster-lisandra-valkyrie',
    name: 'Lisandra — Valkyrie of Di Lorenzo',
    price: '$4',
    description: 'Digital poster, full resolution.',
    image: posterLisandraValkyrie,
    buyLink: 'https://ko-fi.com/s/0a0e7c37e0',
  },
  {
    id: 'poster-odin',
    name: 'Odin — Allfather of Di Lorenzo',
    price: '$4',
    description: 'Digital poster, full resolution.',
    image: posterOdin,
    buyLink: 'https://ko-fi.com/s/e7ed2a8273',
  },
  {
    id: 'poster-dante',
    name: 'Dante — Commander of All Armies of Di Lorenzo',
    price: '$4',
    description: 'Digital poster, full resolution.',
    image: posterDante,
    buyLink: 'https://ko-fi.com/s/c7566b5001',
  },
  {
    id: 'poster-runar',
    name: 'Rúnar — Mad Seer of Di Lorenzo',
    price: '$4',
    description: 'Digital poster, full resolution.',
    image: posterRunar,
    buyLink: 'https://ko-fi.com/s/cc36e618c5',
  },
  {
    id: 'poster-bjorn',
    name: 'Björn — Son of the North of Di Lorenzo',
    price: '$4',
    description: 'Digital poster, full resolution.',
    image: posterBjorn,
    buyLink: 'https://ko-fi.com/s/03784a57af',
  },
]

export default function Shop() {
  useEffect(() => {
    document.title = 'Shop — House of Di Lorenzo'
  }, [])

  return (
    <div className="min-h-screen bg-void px-6 py-16 sm:px-10">
      <div className="mx-auto max-w-2xl text-center">
        <img src={crestIcon} alt="" className="mx-auto mb-8 h-16 w-16 object-contain opacity-95" />
        <p className="eyebrow mb-4">House of Di Lorenzo</p>
        <h1 className="font-display text-4xl text-ivory sm:text-5xl">
          The <span className="gold-text italic">Shop</span>
        </h1>
        <p className="mt-5 font-body text-ivory-dim">
          Digital posters, character sheets, and prompts from the production.
        </p>
      </div>

      <div className="mx-auto mt-14 max-w-5xl">
        {products.length === 0 ? (
          <div className="reveal is-visible text-center">
            <p className="font-body text-sm text-ivory-dim italic">
              Posters, character sheets, and prompts — opening soon. In the meantime:
            </p>
            <a
              href="https://ko-fi.com/houseofdilorenzo/shop"
              target="_blank"
              rel="noreferrer"
              className="btn-gold mt-6 inline-block"
            >
              Visit the Shop on Ko-fi
            </a>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((product) => (
              <a
                key={product.id}
                href={product.buyLink}
                target="_blank"
                rel="noreferrer"
                className="group border border-ink-line bg-ink transition-colors hover:border-gold"
              >
                <img
                  src={product.image}
                  alt={product.name}
                  className="aspect-[2/3] w-full object-cover opacity-90 transition-opacity group-hover:opacity-100"
                />
                <div className="px-5 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-display text-lg text-ivory">{product.name}</p>
                    <p className="shrink-0 font-body text-sm text-gold">{product.price}</p>
                  </div>
                  {product.description && (
                    <p className="mt-2 font-body text-sm text-ivory-dim">{product.description}</p>
                  )}
                </div>
              </a>
            ))}
          </div>
        )}
      </div>

      <p className="mt-16 text-center font-body text-xs tracking-wide text-ivory-dim/70">
        <a href="/" className="text-gold underline underline-offset-4">
          Back to House of Di Lorenzo
        </a>
      </p>
    </div>
  )
}
