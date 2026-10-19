import { useEffect } from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import About from './components/About'
import Services from './components/Services'
import Contact from './components/Contact'
import Footer from './components/Footer'
import useReveal from './hooks/useReveal'

function App() {
  useReveal()

  useEffect(() => {
    document.title = 'William James Creative'
  }, [])

  return (
    <div className="bg-void">
      <Header />
      <main>
        <Hero />
        <About />
        <Services />
        <Contact />
      </main>
      <Footer />
    </div>
  )
}

export default App
