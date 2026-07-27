import SectionDivider from './SectionDivider'

export default function About() {
  return (
    <section id="about" className="bg-void-deep px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-3xl text-center">
        <p className="eyebrow reveal mb-4">Behind House of Di Lorenzo</p>
        <h2 className="reveal font-display text-3xl text-ivory sm:text-4xl">The Filmmaker</h2>

        <SectionDivider />

        <p className="reveal mt-8 font-body text-lg text-ivory-dim">
          I'm a self-taught filmmaker and designer based in Switzerland. What started as a way
          to tell one story turned into a growing universe — and a deep, hands-on mastery of
          video production, fashion design, environment design, character consistency, and
          full episode-scale storytelling, including cinematic soundtrack creation.
        </p>

        <p className="reveal mt-6 font-body text-lg text-ivory-dim">
          Born into a tri-cultural family — Swiss, Latina, and Chinese — I grew up passionate
          about learning from different cultures. I'm fluent in four languages: English,
          Español, Deutsch, and Français.
        </p>

        <div className="reveal mt-10 inline-flex items-center gap-3 border border-gold-dim px-5 py-3">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M12 2 14.5 8.5 21 9.3 16.2 13.8 17.6 20.2 12 17 6.4 20.2 7.8 13.8 3 9.3 9.5 8.5Z"
              stroke="#c9a24a"
              strokeWidth="1"
            />
          </svg>
          <span className="font-body text-sm tracking-wide text-ivory-dim">
            Certified · Higgsfield Academy AI Filmmaking Pipeline
          </span>
        </div>
      </div>
    </section>
  )
}
