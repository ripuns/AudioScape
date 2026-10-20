import Nav from './components/Nav.jsx'
import Hero from './components/Hero.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import Studio from './components/Studio.jsx'
import Environments from './components/Environments.jsx'
import Footer from './components/Footer.jsx'

export default function App() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <Studio />
        <Environments />
      </main>
      <Footer />
    </>
  )
}
