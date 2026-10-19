import { useState, type FormEvent } from 'react'
import SectionDivider from './SectionDivider'

const CONTACT_EMAIL = 'info@houseofdilorenzo.com'

const INSTAGRAM_LINKS = [
  { handle: '@thehouseofdilorenzo', url: 'https://instagram.com/thehouseofdilorenzo' },
  { handle: '@amanda.dilorenzo', url: 'https://instagram.com/amanda.dilorenzo' },
]

const PROJECT_TYPES = ['Trailer', 'Social Content', 'Book Trailer', 'Other']

export default function Contact() {
  const [status, setStatus] = useState<'idle' | 'sent'>('idle')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const subject = encodeURIComponent(`New inquiry — ${form.get('projectType')}`)
    const body = encodeURIComponent(
      `Name: ${form.get('name')}\nEmail: ${form.get('email')}\nProject type: ${form.get('projectType')}\n\n${form.get('message')}`,
    )
    window.location.href = `mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`
    setStatus('sent')
  }

  return (
    <section id="contact" className="bg-void px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-2xl">
        <div className="reveal text-center">
          <p className="eyebrow mb-4">Let's Create Something</p>
          <h2 className="font-display text-3xl text-ivory sm:text-4xl">Get in touch</h2>
          <p className="mt-5 font-body text-ivory-dim">
            Tell me about your project — book, brand, or story — and I'll get back to you with
            a plan and quote.
          </p>
        </div>

        <SectionDivider />

        <form onSubmit={handleSubmit} className="reveal mt-8 grid gap-6">
          <div className="grid gap-6 sm:grid-cols-2">
            <label className="grid gap-2">
              <span className="text-xs tracking-[0.14em] text-ivory-dim uppercase">Name</span>
              <input
                required
                name="name"
                type="text"
                className="border border-ink-line bg-transparent px-4 py-3 font-body text-ivory focus:border-gold"
              />
            </label>
            <label className="grid gap-2">
              <span className="text-xs tracking-[0.14em] text-ivory-dim uppercase">Email</span>
              <input
                required
                name="email"
                type="email"
                className="border border-ink-line bg-transparent px-4 py-3 font-body text-ivory focus:border-gold"
              />
            </label>
          </div>

          <label className="grid gap-2">
            <span className="text-xs tracking-[0.14em] text-ivory-dim uppercase">
              Project type
            </span>
            <select
              required
              name="projectType"
              defaultValue=""
              className="border border-ink-line bg-void px-4 py-3 font-body text-ivory focus:border-gold"
            >
              <option value="" disabled>
                Select one
              </option>
              {PROJECT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>

          <label className="grid gap-2">
            <span className="text-xs tracking-[0.14em] text-ivory-dim uppercase">Message</span>
            <textarea
              required
              name="message"
              rows={5}
              className="border border-ink-line bg-transparent px-4 py-3 font-body text-ivory focus:border-gold"
            />
          </label>

          <button type="submit" className="btn-gold justify-self-start">
            Send Inquiry
          </button>

          {status === 'sent' && (
            <p className="font-body text-sm text-gold-bright" role="status">
              Opening your email client to finish sending — thank you.
            </p>
          )}
        </form>

        <p className="reveal mt-10 text-center font-body text-sm text-ivory-dim">
          Prefer not to fill out a form?{' '}
          <a href={`mailto:${CONTACT_EMAIL}`} className="text-gold underline underline-offset-4">
            Email me directly
          </a>{' '}
          or find me on Instagram —{' '}
          {INSTAGRAM_LINKS.map((link, i) => (
            <span key={link.handle}>
              <a
                href={link.url}
                target="_blank"
                rel="noreferrer"
                className="text-gold underline underline-offset-4"
              >
                {link.handle}
              </a>
              {i < INSTAGRAM_LINKS.length - 1 ? ' or ' : ''}
            </span>
          ))}
          .
        </p>
      </div>
    </section>
  )
}
