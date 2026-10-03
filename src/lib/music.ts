const modules = import.meta.glob('../assets/music/*.{mp3,wav,m4a}', {
  eager: true,
  import: 'default',
}) as Record<string, string>

export type Track = {
  title: string
  src: string
}

function titleFromFilename(path: string) {
  const filename = path.split('/').pop() ?? path
  const withoutExt = filename.replace(/\.[^.]+$/, '')
  const withoutPrefix = withoutExt.replace(/^\d+[\s-]*/, '')
  return withoutPrefix
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export const tracks: Track[] = Object.keys(modules)
  .sort()
  .map((path) => ({
    title: titleFromFilename(path),
    src: modules[path],
  }))
