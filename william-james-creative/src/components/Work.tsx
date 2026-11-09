// TODO(Amanda): real thumbnails/video loops go here once Will sends source
// files — these are gradient placeholders standing in for his actual stills.
// Titles, categories and the Behance link are pulled from his public profile
// (behance.net/williamjames16), so this is already his real body of work.
const PROJECTS = [
  {
    title: 'RED SONJA',
    category: 'AI Music Video',
    href: 'https://www.behance.net/gallery/234511439/RED-SONJA-Ai-Music-Video',
    gradient: 'linear-gradient(135deg, #ff7a3d 0%, #c4132c 100%)',
  },
  {
    title: 'Girls of Kombat',
    category: 'AI Music Video',
    href: 'https://www.behance.net/williamjames16',
    gradient: 'linear-gradient(135deg, #ff9a4d 0%, #e8762f 100%)',
  },
  {
    title: 'Street Fighter Girls',
    category: 'AI Music Video',
    href: 'https://www.behance.net/williamjames16',
    gradient: 'linear-gradient(135deg, #c4132c 0%, #0b0908 100%)',
  },
  {
    title: 'Nicotine Rush',
    category: 'AI Short',
    href: 'https://www.behance.net/williamjames16',
    gradient: 'linear-gradient(135deg, #ff4b1f 0%, #16120f 100%)',
  },
  {
    title: 'The Elegant Siren',
    category: 'AI Music Video — Anniversary',
    href: 'https://www.behance.net/williamjames16',
    gradient: 'linear-gradient(135deg, #e8762f 0%, #c4132c 100%)',
  },
  {
    title: 'Fresh Ink',
    category: 'Luma Dream Brief',
    href: 'https://www.behance.net/williamjames16',
    gradient: 'linear-gradient(135deg, #ff7a3d 0%, #16120f 100%)',
  },
]

export default function Work() {
  return (
    <section id="work" className="bg-void px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-5xl">
        <p className="eyebrow reveal mb-4">Selected Work</p>
        <h2 className="reveal max-w-2xl font-display text-3xl leading-tight font-black text-ivory sm:text-4xl">
          AI-directed video and character art, built for the screen.
        </h2>

        <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {PROJECTS.map((project) => (
            <a
              key={project.title}
              href={project.href}
              target="_blank"
              rel="noopener noreferrer"
              className="reveal group block overflow-hidden rounded-xl border border-ink-line"
            >
              <div
                className="flex aspect-video items-end p-5 transition-transform duration-300 group-hover:scale-105"
                style={{ background: project.gradient }}
              >
                <div>
                  <p className="font-display text-lg font-black text-ivory drop-shadow-[0_1px_8px_rgba(0,0,0,0.5)]">
                    {project.title}
                  </p>
                  <p className="mt-1 text-xs tracking-wide text-ivory/80 uppercase">
                    {project.category}
                  </p>
                </div>
              </div>
            </a>
          ))}
        </div>

        <p className="reveal mt-10 text-center">
          <a
            href="https://www.behance.net/williamjames16"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-bold text-ember-bright underline underline-offset-4 hover:text-ember"
          >
            View full portfolio on Behance →
          </a>
        </p>
      </div>
    </section>
  )
}
