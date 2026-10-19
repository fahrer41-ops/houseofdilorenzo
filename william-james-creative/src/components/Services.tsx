// TODO(Amanda): placeholder service list — common offerings for this kind of
// creative-portfolio site. Swap for whatever Will actually does.
const SERVICES = [
  { number: '01', title: 'Brand Identity' },
  { number: '02', title: 'Web Design' },
  { number: '03', title: 'Art Direction' },
  { number: '04', title: 'Content Design' },
]

export default function Services() {
  return (
    <section id="services" className="bg-void px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <p className="eyebrow reveal mb-4">What I Do</p>
        <h2 className="reveal max-w-2xl font-display text-3xl leading-tight font-black text-ivory sm:text-4xl">
          Design expertise to turn ideas into{' '}
          <span className="ember-gradient-text">work that lands.</span>
        </h2>

        <div className="mt-16 divide-y divide-ink-line border-t border-b border-ink-line">
          {SERVICES.map((service) => (
            <div
              key={service.number}
              className="reveal flex items-center gap-6 py-6 transition-colors hover:bg-ink"
            >
              <span className="font-display text-3xl font-black text-ember/70 sm:text-4xl">
                {service.number}
              </span>
              <span className="font-display text-xl font-bold text-ivory sm:text-2xl">
                {service.title}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
