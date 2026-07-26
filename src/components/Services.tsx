import SectionDivider from './SectionDivider'

const SERVICES = [
  {
    title: 'Promotional Trailers & Teasers',
    body: 'Short-form hooks built to stop the scroll — for books, brands, or original concepts.',
  },
  {
    title: 'Social Media Video Content',
    body: 'Character-consistent short-form content for Instagram, TikTok, and YouTube Shorts.',
  },
  {
    title: 'Book & Story Trailers',
    body: 'Bring a manuscript, series, or fictional world to life before a single reader opens the book.',
  },
]

export default function Services() {
  return (
    <section id="services" className="bg-void-deep px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">What I Create</p>
          <h2 className="font-display text-3xl text-ivory sm:text-4xl">Services</h2>
        </div>

        <SectionDivider />

        <div className="mt-8 grid gap-px overflow-hidden border border-ink-line bg-ink-line sm:grid-cols-3">
          {SERVICES.map((service) => (
            <div key={service.title} className="reveal bg-void-deep p-8 sm:p-10">
              <span
                className="mb-6 block h-px w-10 bg-gold"
                aria-hidden="true"
              />
              <h3 className="font-display text-xl text-gold-bright">{service.title}</h3>
              <p className="mt-4 font-body text-ivory-dim">{service.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
