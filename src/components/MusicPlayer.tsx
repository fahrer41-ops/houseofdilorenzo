import { useRef, useState } from 'react'
import type { Track } from '../lib/music'

function NoteIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
      <path d="M9 18V5l12-2v13" stroke="currentColor" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="6" cy="18" r="3" stroke="currentColor" strokeWidth="1.6" fill="none" />
      <circle cx="18" cy="16" r="3" stroke="currentColor" strokeWidth="1.6" fill="none" />
    </svg>
  )
}

function PlayGlyph() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
      <path d="M8 5v14l11-7z" />
    </svg>
  )
}

function PauseGlyph() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
      <rect x="6" y="5" width="4" height="14" />
      <rect x="14" y="5" width="4" height="14" />
    </svg>
  )
}

function TrackRow({
  track,
  isActive,
  isPlaying,
  onToggle,
}: {
  track: Track
  isActive: boolean
  isPlaying: boolean
  onToggle: () => void
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="reveal group flex w-full items-center gap-4 border-b border-ink-line py-4 text-left transition-colors hover:bg-ink/40"
    >
      <span
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full border transition-colors ${
          isActive ? 'border-gold text-gold-bright' : 'border-gold-dim text-gold group-hover:border-gold'
        }`}
      >
        {isActive && isPlaying ? <PauseGlyph /> : <PlayGlyph />}
      </span>
      <span className="flex items-center gap-2 font-body text-ivory">
        <NoteIcon />
        {track.title}
      </span>
    </button>
  )
}

export default function MusicPlayer({ tracks }: { tracks: Track[] }) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  function handleToggle(index: number) {
    if (activeIndex === index) {
      if (isPlaying) {
        audioRef.current?.pause()
        setIsPlaying(false)
      } else {
        audioRef.current?.play()
        setIsPlaying(true)
      }
      return
    }
    setActiveIndex(index)
    setIsPlaying(true)
  }

  if (tracks.length === 0) {
    return (
      <p className="reveal font-body text-sm text-ivory-dim italic">More soundtracks coming soon.</p>
    )
  }

  return (
    <div>
      {tracks.map((track, i) => (
        <TrackRow
          key={track.src}
          track={track}
          isActive={activeIndex === i}
          isPlaying={isPlaying}
          onToggle={() => handleToggle(i)}
        />
      ))}
      {activeIndex !== null && (
        <audio
          ref={audioRef}
          src={tracks[activeIndex].src}
          autoPlay
          controls
          controlsList="nodownload noremoteplayback"
          onContextMenu={(e) => e.preventDefault()}
          onEnded={() => setIsPlaying(false)}
          className="reveal is-visible mt-4 w-full"
        />
      )}
    </div>
  )
}
