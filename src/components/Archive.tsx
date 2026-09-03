import { useState } from 'react'
import GalleryLightbox from './GalleryLightbox'
import MusicPlayer from './MusicPlayer'
import SectionDivider from './SectionDivider'
import Watermark from './Watermark'
import { galleries } from '../lib/galleries'
import { tracks } from '../lib/music'

function GalleryPreviewGrid({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false)
  const gallery = galleries[slug]

  if (!gallery || gallery.images.length === 0) {
    return (
      <div className="reveal flex aspect-square w-full max-w-40 items-center justify-center border border-ink-line bg-ink">
        <p className="font-body text-sm text-ivory-dim italic">Coming soon</p>
      </div>
    )
  }

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {gallery.images.slice(0, 8).map((src, i) => (
          <button
            key={src}
            type="button"
            onClick={() => setOpen(true)}
            className="reveal group relative aspect-square overflow-hidden border border-ink-line bg-ink"
          >
            <img
              src={src}
              alt=""
              draggable={false}
              onContextMenu={(e) => e.preventDefault()}
              className="h-full w-full select-none object-cover transition-transform duration-700 ease-out group-hover:scale-105"
            />
            <Watermark />
            {i === 7 && gallery.images.length > 8 && (
              <div className="absolute inset-0 flex items-center justify-center bg-void/70">
                <span className="font-display text-lg text-ivory">+{gallery.images.length - 7}</span>
              </div>
            )}
          </button>
        ))}
      </div>
      {open && (
        <GalleryLightbox
          title={gallery.title}
          images={gallery.images}
          startIndex={0}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  )
}

export default function Archive() {
  return (
    <section id="archive" className="bg-void-deep px-6 py-28 sm:px-10">
      <div className="mx-auto max-w-6xl">
        <div className="reveal mx-auto max-w-2xl text-center">
          <p className="eyebrow mb-4">The Archive</p>
          <h2 className="font-display text-3xl text-ivory sm:text-4xl">
            Behind the <span className="gold-text italic">craft</span>
          </h2>
          <p className="mt-5 font-body text-ivory-dim">
            Original design work and soundtracks from both worlds — shared here for viewing and
            listening. All rights reserved; for licensing or usage inquiries, reach out directly.
          </p>
        </div>

        <SectionDivider />

        <div className="mt-8">
          <h3 className="reveal mb-6 font-display text-2xl text-gold-bright">Wardrobe</h3>
          <GalleryPreviewGrid slug="wardrobe" />
        </div>

        <div className="mt-20">
          <h3 className="reveal mb-6 font-display text-2xl text-gold-bright">Worlds &amp; Environment</h3>
          <GalleryPreviewGrid slug="worlds-environment" />
        </div>

        <div className="mt-20">
          <h3 className="reveal mb-6 font-display text-2xl text-gold-bright">Music</h3>
          <MusicPlayer tracks={tracks} />
        </div>
      </div>
    </section>
  )
}
