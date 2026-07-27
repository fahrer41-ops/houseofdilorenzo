import { useEffect, useState } from 'react'

type GalleryLightboxProps = {
  title: string
  images: string[]
  startIndex: number
  onClose: () => void
}

export default function GalleryLightbox({ title, images, startIndex, onClose }: GalleryLightboxProps) {
  const [index, setIndex] = useState(startIndex)

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowRight') setIndex((i) => (i + 1) % images.length)
      if (e.key === 'ArrowLeft') setIndex((i) => (i - 1 + images.length) % images.length)
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [images.length, onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-void-deep/96 p-4 sm:p-10"
      onClick={onClose}
    >
      <div className="mb-4 flex w-full max-w-4xl items-center justify-between">
        <p className="font-display text-lg text-ivory sm:text-xl">
          {title} <span className="text-ivory-dim">· {index + 1}/{images.length}</span>
        </p>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close gallery"
          className="flex h-9 w-9 items-center justify-center rounded-full border border-gold-dim text-gold transition-colors hover:border-gold hover:text-gold-bright"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 4l16 16M20 4L4 20" strokeLinecap="round" />
          </svg>
        </button>
      </div>

      <div className="relative flex w-full max-w-4xl flex-1 items-center justify-center" onClick={(e) => e.stopPropagation()}>
        {images.length > 1 && (
          <button
            type="button"
            aria-label="Previous image"
            onClick={() => setIndex((i) => (i - 1 + images.length) % images.length)}
            className="absolute left-0 flex h-10 w-10 items-center justify-center rounded-full border border-gold-dim text-gold transition-colors hover:border-gold hover:text-gold-bright sm:-left-14"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 5l-7 7 7 7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        )}
        <img
          src={images[index]}
          alt=""
          className="max-h-[75vh] max-w-full object-contain"
        />
        {images.length > 1 && (
          <button
            type="button"
            aria-label="Next image"
            onClick={() => setIndex((i) => (i + 1) % images.length)}
            className="absolute right-0 flex h-10 w-10 items-center justify-center rounded-full border border-gold-dim text-gold transition-colors hover:border-gold hover:text-gold-bright sm:-right-14"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        )}
      </div>

      {images.length > 1 && (
        <div className="mt-4 flex max-w-full gap-2 overflow-x-auto pb-1">
          {images.map((src, i) => (
            <button
              key={src}
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                setIndex(i)
              }}
              className={`h-14 w-14 flex-shrink-0 overflow-hidden border transition-colors ${
                i === index ? 'border-gold' : 'border-ink-line opacity-60 hover:opacity-100'
              }`}
            >
              <img src={src} alt="" className="h-full w-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
