const modules = import.meta.glob('../assets/gallery/*/*.{jpg,jpeg,png,webp}', {
  eager: true,
  import: 'default',
}) as Record<string, string>

export type Gallery = {
  slug: string
  title: string
  images: string[]
}

function titleCase(slug: string) {
  return slug
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const bySlug = new Map<string, string[]>()

for (const path of Object.keys(modules).sort()) {
  const match = path.match(/gallery\/([^/]+)\//)
  if (!match) continue
  const slug = match[1]
  if (!bySlug.has(slug)) bySlug.set(slug, [])
  bySlug.get(slug)!.push(modules[path])
}

export const galleries: Record<string, Gallery> = {}
for (const [slug, images] of bySlug) {
  galleries[slug] = { slug, title: titleCase(slug), images }
}
