import { readdirSync, statSync } from 'node:fs'
import { extname, join } from 'node:path'
import sharp from 'sharp'

const TARGET_DIRS = ['src/assets/gallery']
const MAX_WIDTH = 1800
const JPEG_QUALITY = 85
const IMAGE_EXTENSIONS = new Set(['.jpg', '.jpeg', '.png', '.webp'])

function walk(dir) {
  const files = []
  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry)
    const stat = statSync(fullPath)
    if (stat.isDirectory()) files.push(...walk(fullPath))
    else if (IMAGE_EXTENSIONS.has(extname(entry).toLowerCase())) files.push(fullPath)
  }
  return files
}

async function optimize(path) {
  const before = statSync(path).size
  const ext = extname(path).toLowerCase()
  const image = sharp(path)
  const metadata = await image.metadata()

  if (metadata.width && metadata.width > MAX_WIDTH) {
    image.resize({ width: MAX_WIDTH })
  }

  if (ext === '.png') {
    image.png({ compressionLevel: 9, adaptiveFiltering: true })
  } else if (ext === '.webp') {
    image.webp({ quality: JPEG_QUALITY })
  } else {
    image.jpeg({ quality: JPEG_QUALITY, mozjpeg: true })
  }

  const buffer = await image.toBuffer()
  if (buffer.length < before) {
    const { writeFileSync } = await import('node:fs')
    writeFileSync(path, buffer)
    console.log(`optimized ${path}: ${(before / 1024).toFixed(0)}kb -> ${(buffer.length / 1024).toFixed(0)}kb`)
  } else {
    console.log(`skipped ${path}: already optimal`)
  }
}

for (const dir of TARGET_DIRS) {
  let files = []
  try {
    files = walk(dir)
  } catch {
    continue
  }
  for (const file of files) {
    await optimize(file)
  }
}
