export default function Footer() {
  return (
    <footer className="border-t border-blush-deep bg-cream px-6 py-10 text-center sm:px-10">
      <p className="font-display text-lg italic text-plum">
        Manu <span className="gold-text not-italic">Cakes</span>
      </p>
      <p className="mt-2 font-body text-xs tracking-wide text-plum-dim/70">
        Sargans, Svizzera · &copy; {new Date().getFullYear()} Manuela Climonxa
      </p>
    </footer>
  )
}
