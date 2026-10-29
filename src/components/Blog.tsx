import { useEffect } from 'react'
import { blogPosts } from '../lib/blogPosts'

function formatDate(iso: string) {
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function Blog() {
  useEffect(() => {
    document.title = 'Blog — House of Di Lorenzo'
  }, [])

  const posts = [...blogPosts].sort((a, b) => b.date.localeCompare(a.date))

  return (
    <div className="min-h-screen bg-void">
      <div className="mx-auto max-w-2xl px-6 pt-32 pb-4 text-center sm:px-10">
        <p className="eyebrow mb-4">House of Di Lorenzo</p>
        <h1 className="font-display text-4xl leading-[1.1] text-ivory sm:text-5xl md:text-6xl">
          The <span className="gold-text italic">Blog</span>
        </h1>
        <p className="mt-5 font-body text-lg text-ivory-dim italic">
          The story behind the story.
        </p>
      </div>

      <div className="mx-auto mt-14 flex max-w-2xl flex-col gap-10 px-6 pb-20 sm:px-10">
        {posts.length === 0 ? (
          <p className="text-center font-body text-sm text-ivory-dim italic">Posts coming soon.</p>
        ) : (
          posts.map((post) => (
            <a
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="group block border border-ink-line bg-ink px-7 py-8 transition-colors hover:border-gold-dim"
            >
              <p className="eyebrow mb-3">{formatDate(post.date)}</p>
              <h2 className="font-display text-2xl text-ivory transition-colors group-hover:text-gold-bright sm:text-3xl">
                {post.title}
              </h2>
              <p className="mt-3 font-body text-ivory-dim">{post.excerpt}</p>
              <p className="mt-5 font-body text-sm tracking-[0.1em] text-gold uppercase">
                Read &rarr;
              </p>
            </a>
          ))
        )}
      </div>

      <p className="px-6 pb-16 text-center font-body text-xs tracking-wide text-ivory-dim/70 sm:px-10">
        <a href="/" className="text-gold underline underline-offset-4">
          Back to House of Di Lorenzo
        </a>
      </p>
    </div>
  )
}
