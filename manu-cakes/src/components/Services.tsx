const services = [
  {
    title: 'Torte Nuziali',
    description: 'Creazioni eleganti su misura per il giorno più importante, dal bozzetto al taglio della torta.',
  },
  {
    title: 'Torte di Compleanno',
    description: 'Dai classici più raffinati ai temi più creativi per i più piccoli — ogni età, ogni stile.',
  },
  {
    title: 'Torte Personalizzate',
    description: 'Hai un’idea in mente? La realizziamo insieme, su misura per la tua occasione.',
  },
  {
    title: 'Buffet di Dolci',
    description: 'Tavoli di dolci e composizioni per eventi, feste e ricorrenze.',
  },
  {
    title: 'Opzioni Senza Glutine',
    description: 'Creazioni gluten-free, senza rinunciare al gusto e alla bellezza.',
  },
]

export default function Services() {
  return (
    <section id="services" className="bg-cream px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">Servizi</p>
          <h2 className="font-display text-3xl text-plum sm:text-4xl">
            Per ogni <span className="gold-text italic">occasione</span>
          </h2>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <div
              key={service.title}
              className="reveal border border-blush-deep bg-blush px-7 py-8 transition-colors hover:border-rose"
            >
              <h3 className="font-display text-xl text-plum">{service.title}</h3>
              <p className="mt-3 font-body text-sm leading-relaxed text-plum-dim">{service.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
