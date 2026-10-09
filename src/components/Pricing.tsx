import SectionDivider from './SectionDivider'

const TIERS = [
  {
    name: 'Short Teaser',
    length: '10–15 seconds, single scene',
    price: 'CHF 150–250',
  },
  {
    name: 'Story Trailer',
    length: '30–60 seconds, multi-shot',
    price: 'CHF 300–600',
  },
  {
    name: 'Full Narrative Piece',
    length: 'Complex multi-character sequences',
    price: 'CHF 600–1,200+',
  },
]

export default function Pricing() {
  return (
    <section id="pricing" className="bg-void px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-4xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">Investment</p>
          <h2 className="font-display text-3xl text-ivory sm:text-4xl">
            Starting <span className="gold-text italic">prices</span>
          </h2>
        </div>

        <SectionDivider />

        <div className="reveal mt-8 border border-ink-line">
          {TIERS.map((tier, i) => (
            <div
              key={tier.name}
              className={`grid grid-cols-1 gap-2 px-6 py-6 sm:grid-cols-[1.2fr_1.6fr_1fr] sm:items-center sm:gap-6 sm:px-10 ${
                i !== TIERS.length - 1 ? 'border-b border-ink-line' : ''
              }`}
            >
              <h3 className="font-display text-xl text-gold-bright">{tier.name}</h3>
              <p className="font-body text-ivory-dim">{tier.length}</p>
              <p className="font-display text-lg text-ivory sm:text-right">{tier.price}</p>
            </div>
          ))}
        </div>

        <p className="reveal mt-6 text-center font-body text-sm text-ivory-dim italic">
          Final pricing depends on complexity and length. Every project includes
          character-consistency design, professional color grading, and unlimited minor
          revisions.
        </p>
      </div>
    </section>
  )
}
