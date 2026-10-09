import heroCake from '../assets/hero-heart-cake.jpg'

export default function Hero() {
  return (
    <section id="top" className="relative flex min-h-screen items-center overflow-hidden bg-blush pt-24">
      <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 sm:px-10 lg:grid-cols-2">
        <div className="reveal is-visible text-center lg:text-left">
          <p className="eyebrow mb-5">Torte Artigianali · Sargans</p>
          <h1 className="font-display text-4xl leading-[1.12] text-plum sm:text-5xl md:text-6xl">
            Dolci che <span className="gold-text italic">raccontano</span> emozioni
          </h1>
          <p className="mx-auto mt-6 max-w-md font-body text-lg text-plum-dim lg:mx-0">
            Creazioni artigianali realizzate con passione — torte nuziali, compleanni e momenti
            speciali, fatte a mano da Manuela, a Sargans.
          </p>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center lg:justify-start">
            <a href="https://instagram.com/manu.cakes78" target="_blank" rel="noreferrer" className="btn-rose">
              Scrivimi su Instagram
            </a>
            <a href="#gallery" className="btn-ghost">
              Guarda le Creazioni
            </a>
          </div>
        </div>

        <div className="reveal is-visible">
          <div className="overflow-hidden rounded-[2rem] border border-blush-deep shadow-xl shadow-rose/10">
            <img src={heroCake} alt="Torta nuziale Manu Cakes, con cuore di fiori" className="w-full object-cover" />
          </div>
        </div>
      </div>
    </section>
  )
}
