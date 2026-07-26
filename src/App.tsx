import About from './components/About'
import Contact from './components/Contact'
import Footer from './components/Footer'
import Header from './components/Header'
import Hero from './components/Hero'
import useReveal from './hooks/useReveal'
import Pricing from './components/Pricing'
import Portfolio from './components/Portfolio'
import Services from './components/Services'

function App() {
  useReveal()

  return (
    <div className="bg-void">
      <Header />
      <main>
        <Hero />
        <Portfolio />
        <Services />
        <Pricing />
        <About />
        <Contact />
      </main>
      <Footer />
    </div>
  )
}

export default App
