// TODO(Amanda): swap the placeholder email/social links once Will shares his
// preferred contact details.
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
        <a href="mailto:hello@williamjamescreative.com" className="reveal btn-ember mt-9 inline-flex">
          hello@williamjamescreative.com
        </a>
      </div>
    </section>
  )
}
