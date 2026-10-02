import { useEffect } from 'react'
import crestIcon from '../assets/crest-icon.png'

// TODO(Amanda): once you've got a Ko-fi/Buy Me a Coffee shop (or
// whatever platform you land on) set up, send me each product's name,
// price, image, and buy link, and I'll drop them in here.
type Product = {
  id: string
  name: string
  price: string
  image: string
  buyLink: string
}

const products: Product[] = []

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
                  className="aspect-square w-full object-cover opacity-90 transition-opacity group-hover:opacity-100"
                />
                <div className="flex items-center justify-between px-5 py-4">
                  <p className="font-display text-lg text-ivory">{product.name}</p>
                  <p className="font-body text-sm text-gold">{product.price}</p>
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
