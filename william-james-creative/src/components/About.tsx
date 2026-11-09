export default function About() {
  return (
    <section id="about" className="bg-ivory px-6 py-28 text-void sm:px-10">
      <div className="mx-auto max-w-5xl">
        <h2 className="reveal text-center font-display text-4xl font-black tracking-tight sm:text-5xl">
          ABOUT
        </h2>

        <div className="mt-16 grid grid-cols-1 items-center gap-10 sm:grid-cols-[1fr_auto_1fr]">
          <p className="reveal text-right font-display text-3xl font-black sm:text-4xl">THINK</p>
          <div className="reveal mx-auto aspect-video w-full max-w-sm overflow-hidden rounded-xl bg-gradient-to-br from-ember-bright to-ember-deep sm:w-80" />
          <p className="reveal font-display text-3xl font-black text-ember sm:text-4xl">BOLD.</p>
        </div>

        {/* TODO(Amanda): placeholder bio — swap once Will sends real copy. */}
        <p className="reveal mx-auto mt-14 max-w-xl text-center font-body text-black/60">
          William is a designer and art director focused on building brands and digital products
          that feel considered, not templated. This paragraph is a placeholder — swap it for his
          real bio once it lands.
        </p>
      </div>
    </section>
  )
}
