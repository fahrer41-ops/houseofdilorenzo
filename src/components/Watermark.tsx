const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='320' height='160'>
  <text x='-20' y='95' font-family='Georgia, serif' font-size='19' letter-spacing='2' fill='#c9a24a' fill-opacity='0.4' transform='rotate(-28 160 80)'>HOUSE OF DI LORENZO</text>
</svg>`

const backgroundImage = `url("data:image/svg+xml,${encodeURIComponent(svg)}")`

export default function Watermark() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-0 z-10"
      style={{ backgroundImage, backgroundRepeat: 'repeat' }}
    />
  )
}
