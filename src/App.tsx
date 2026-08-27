import About from './components/About'
import Archive from './components/Archive'
import Contact from './components/Contact'
import Footer from './components/Footer'
import Friends from './components/Friends'
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
        <Archive />
        <Friends />
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
