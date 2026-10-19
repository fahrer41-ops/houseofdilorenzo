function InstagramIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.2" cy="6.8" r="0.6" fill="currentColor" stroke="none" />
    </svg>
  )
}

// TODO(Amanda): swap the placeholder email once Will shares a preferred
// contact address — Instagram is his real handle.
export default function Contact() {
  return (
    <section id="contact" className="bg-void px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-2xl text-center">
        <p className="eyebrow reveal mb-4">Get in Touch</p>
        <h2 className="reveal font-display text-3xl font-black text-ivory sm:text-4xl">
          Let's build <span className="ember-gradient-text italic">something real.</span>
        </h2>
        <p className="reveal mt-5 font-body text-ivory-dim">
          Open to new projects — reach out and let's talk about what you need.
        </p>
        <div className="reveal mt-9 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <a href="mailto:hello@williamjamescreative.com" className="btn-ember">
            hello@williamjamescreative.com
          </a>
          <a
            href="https://www.instagram.com/williamjamesb166er"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost"
          >
            <InstagramIcon />
            @williamjamesb166er
          </a>
        </div>
      </div>
    </section>
  )
}
