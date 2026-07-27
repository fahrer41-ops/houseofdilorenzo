import { useState } from 'react'
import baliImage from '../assets/bali-reddress.jpg'
import empireAftermath from '../assets/empire-aftermath.jpg'
import empireDuo from '../assets/empire-duo.jpg'
import empireEye from '../assets/empire-eye.jpg'
import empireWarrior from '../assets/empire-warrior.jpg'
import hallwayImage from '../assets/hallway-barefoot.jpg'
import hospitalImage from '../assets/hospital-reveal.jpg'
import empireImage1 from '../assets/rise-of-empire-1.jpg'
import empireImage2 from '../assets/rise-of-empire-2.jpg'
import SectionDivider from './SectionDivider'

type Reel = {
  image: string
  caption: string
  video?: string
}

const trackOne: Reel[] = [
  { image: hospitalImage, caption: 'The hospital arc reveal', video: '/portfolio/hospital-reveal.mp4' },
  { image: baliImage, caption: 'The Bali honeymoon', video: '/portfolio/bali-honeymoon.mp4' },
  { image: hallwayImage, caption: 'Tenerezza', video: '/portfolio/tenerezza.mp4' },
]

const trackTwo: Reel[] = [
  { image: empireImage2, caption: 'Rise of the Empire — the standoff' },
  { image: empireImage1, caption: 'Rise of the Empire — the guardian' },
  {
    image: empireAftermath,
    caption: 'Rise of the Empire — the aftermath',
    video: '/portfolio/empire-aftermath.mp4',
  },
  {
    image: empireWarrior,
    caption: 'Rise of the Empire — the warrior',
    video: '/portfolio/empire-warrior.mp4',
  },
  { image: empireDuo, caption: 'Rise of the Empire — the alliance', video: '/portfolio/empire-duo.mp4' },
  { image: empireEye, caption: 'Rise of the Empire — the reckoning', video: '/portfolio/empire-eye.mp4' },
]

function ReelCard({ reel }: { reel: Reel }) {
  const [isPlaying, setIsPlaying] = useState(false)

  if (isPlaying && reel.video) {
    return (
      <div className="reveal is-visible relative aspect-[9/16] overflow-hidden border border-ink-line bg-ink">
        <video
          src={reel.video}
          poster={reel.image}
          autoPlay
          controls
          playsInline
          className="h-full w-full object-cover"
        />
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={() => reel.video && setIsPlaying(true)}
      aria-label={reel.video ? `Play — ${reel.caption}` : reel.caption}
      className={`reveal group relative aspect-[9/16] overflow-hidden border border-ink-line bg-ink text-left ${reel.video ? 'cursor-pointer' : 'cursor-default'}`}
    >
      <img
        src={reel.image}
        alt=""
        className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-void/90 via-void/10 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 flex items-center justify-between p-4">
        <span className="font-body text-sm tracking-wide text-ivory">{reel.caption}</span>
        {reel.video && (
          <span className="flex h-9 w-9 items-center justify-center rounded-full border border-gold-dim text-gold transition-colors group-hover:border-gold group-hover:text-gold-bright">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z" />
            </svg>
          </span>
        )}
      </div>
    </button>
  )
}

export default function Portfolio() {
  return (
    <section id="work" className="bg-void px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">The Work</p>
          <h2 className="font-display text-3xl text-ivory sm:text-4xl">
            Two worlds, <span className="gold-text italic">one craft</span>
          </h2>
          <p className="mt-5 font-body text-ivory-dim">
            Contemporary drama and epic fantasy, both built with the same obsessive attention
            to consistency and story.
          </p>
        </div>

        <SectionDivider />

        <div className="mt-8">
          <div className="reveal mb-8 flex items-baseline justify-between gap-4">
            <h3 className="font-display text-2xl text-gold-bright">House of Di Lorenzo</h3>
            <p className="max-w-xs text-right font-body text-sm text-ivory-dim italic sm:max-w-sm">
              Contemporary romance — character-driven, emotionally grounded, cinematic
              realism.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {trackOne.map((reel, i) => (
              <ReelCard reel={reel} key={i} />
            ))}
          </div>
        </div>

        <div className="mt-20">
          <div className="reveal mb-8 flex items-baseline justify-between gap-4">
            <h3 className="font-display text-2xl text-gold-bright">Rise of the Empire</h3>
            <p className="max-w-xs text-right font-body text-sm text-ivory-dim italic sm:max-w-sm">
              Epic fantasy — Vikings, dragons, war, and quiet aftermath.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {trackTwo.map((reel, i) => (
              <ReelCard reel={reel} key={i} />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
