import { useEffect, useState } from 'react'
import crestIcon from '../assets/crest-icon.png'

const ONLYFANS_URL = 'https://onlyfans.com/thehyliangodess?rec=586003470'
// TODO(Amanda): replace with your real Fanvue profile URL.
const FANVUE_URL = 'https://fanvue.com/REPLACE_ME'

export default function Exclusive() {
  const [confirmed, setConfirmed] = useState(false)

  useEffect(() => {
    document.title = 'House of Di Lorenzo — Exclusive'
    const meta = document.createElement('meta')
    meta.name = 'robots'
    meta.content = 'noindex, nofollow'
    document.head.appendChild(meta)
    return () => {
      document.head.removeChild(meta)
    }
  }, [])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-void px-6 py-16 text-center">
      <img src={crestIcon} alt="" className="mb-8 h-16 w-16 object-contain opacity-95" />

      {!confirmed ? (
        <>
          <p className="eyebrow mb-4">18+ Only</p>
          <h1 className="max-w-xl font-display text-3xl text-ivory sm:text-4xl">
            This content is <span className="gold-text italic">strictly adult</span>
          </h1>
          <p className="mt-5 max-w-md font-body text-ivory-dim">
            By entering, you confirm you are at least 18 years old and consent to viewing
            explicit adult content.
          </p>
          <div className="mt-10 flex flex-col gap-4 sm:flex-row">
            <button type="button" onClick={() => setConfirmed(true)} className="btn-gold">
              I am 18+ — Enter
            </button>
            <a href="https://houseofdilorenzo.com" className="btn-ghost">
              Exit
            </a>
          </div>
        </>
      ) : (
        <>
          <p className="eyebrow mb-4">Exclusive</p>
          <h1 className="max-w-xl font-display text-3xl text-ivory sm:text-4xl">
            The <span className="gold-text italic">uncut</span> stories
          </h1>
          <p className="mt-5 max-w-md font-body text-ivory-dim">
            Full, unrestricted scenes from the House of Di Lorenzo universe — available on my
            subscription platforms.
          </p>
          <div className="mt-10 flex flex-col gap-4 sm:flex-row">
            <a href={ONLYFANS_URL} target="_blank" rel="noreferrer" className="btn-gold">
              OnlyFans
            </a>
            <a href={FANVUE_URL} target="_blank" rel="noreferrer" className="btn-gold">
              Fanvue
            </a>
          </div>
        </>
      )}
    </div>
  )
}
