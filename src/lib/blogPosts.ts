export type BlogPost = {
  slug: string
  title: string
  date: string // e.g. '2026-10-29'
  excerpt: string
  // Paragraphs of body copy. Keep it simple text for now — no markdown
  // parsing needed, each string in the array renders as its own <p>.
  body: string[]
}

// TODO(Amanda): replace this placeholder with your real posts from the
// Higgsfield blog. Send me the text for each one (title + date + the
// paragraphs) and I'll add them here in this same shape — newest first.
export const blogPosts: BlogPost[] = [
  {
    slug: 'welcome',
    title: 'Welcome',
    date: '2026-10-29',
    excerpt: 'A space for the parts of the story that don’t fit in a caption.',
    body: [
      'This is where I’ll be writing — slower, longer, more honest than a social post ever has room for. Behind-the-scenes of the franchise, the real story behind House of Di Lorenzo, and whatever else doesn’t fit in a caption.',
      'More soon.',
    ],
  },
]

export function getPostBySlug(slug: string) {
  return blogPosts.find((p) => p.slug === slug)
}
