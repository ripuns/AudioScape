import { useEffect, useState } from 'react'
import { Icon, Logo } from './icons.jsx'

const LINKS = [['How it works', '#how'], ['Studio', '#studio'], ['Environments', '#environments']]

export default function Nav() {
  const [solid, setSolid] = useState(false)
  useEffect(() => {
    const on = () => setSolid(window.scrollY > 24)
    on()
    window.addEventListener('scroll', on, { passive: true })
    return () => window.removeEventListener('scroll', on)
  }, [])

  return (
    <header className={`nav${solid ? ' solid' : ''}`}>
      <div className="nav-in">
        <a className="brand" href="#top" aria-label="AudioScape home"><Logo /><span>AudioScape</span></a>
        <nav aria-label="Primary">
          {LINKS.map(([t, h]) => <a key={h} href={h}>{t}</a>)}
        </nav>
        <div className="nav-cta">
          <a className="icon-link" href="https://github.com/ripuns/AudioScape" target="_blank" rel="noreferrer" aria-label="GitHub repository">
            <Icon name="github" />
          </a>
          <a className="btn btn-sm" href="#studio">Try it <Icon name="arrow" size={16} /></a>
        </div>
      </div>
    </header>
  )
}
