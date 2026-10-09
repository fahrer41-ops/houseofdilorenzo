import { useEffect } from 'react'
import Header from '../components/Header'
import Hero from '../components/Hero'
import Gallery from '../components/Gallery'
import About from '../components/About'
import Services from '../components/Services'
import Contact from '../components/Contact'
import Footer from '../components/Footer'
import useReveal from '../hooks/useReveal'

export default function CakesHome() {
  useReveal()

  useEffect(() => {
    document.title = 'Manu Cakes — Sargans'
  }, [])

  return (
    <div className="bg-cream">
      <Header />
      <main>
        <Hero />
        <Gallery />
        <About />
        <Services />
        <Contact />
      </main>
      <Footer />
    </div>
  )
}
