import { useEffect } from 'react'
import { getPostBySlug } from '../lib/blogPosts'

function formatDate(iso: string) {
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function BlogPost({ slug }: { slug: string }) {
  const post = getPostBySlug(slug)

  useEffect(() => {
    document.title = post ? `${post.title} — House of Di Lorenzo` : 'Blog — House of Di Lorenzo'
  }, [post])

  if (!post) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-void px-6 text-center">
        <h1 className="font-display text-3xl text-ivory">Post not found</h1>
        <a href="/blog" className="btn-ghost mt-8">
          Back to the Blog
        </a>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-void">
      <article className="mx-auto max-w-2xl px-6 pt-32 pb-20 sm:px-10">
        <p className="eyebrow mb-4 text-center">{formatDate(post.date)}</p>
        <h1 className="text-center font-display text-4xl leading-[1.1] text-ivory sm:text-5xl">
          {post.title}
        </h1>

        <div className="hairline my-12" />

        <div className="flex flex-col gap-6 font-body text-lg leading-relaxed text-ivory-dim">
          {post.body.map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
        </div>

        <p className="mt-16 text-center font-body text-xs tracking-wide text-ivory-dim/70">
          <a href="/blog" className="text-gold underline underline-offset-4">
            Back to the Blog
          </a>
        </p>
      </article>
    </div>
  )
}
