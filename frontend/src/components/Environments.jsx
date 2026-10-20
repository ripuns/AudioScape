import { useEffect, useState } from 'react'
import { Icon, soundIcon } from './icons.jsx'
import { useReveal } from '../useReveal.js'

// accent hue per environment for the card glow
const HUE = { beach: 28, forest: 140, classroom: 48, city: 215, cafe: 22, stadium: 350, park: 100, rainy_street: 230 }

export default function Environments() {
  const [cfg, setCfg] = useState(null)
  const [ref, shown] = useReveal(0.1)

  useEffect(() => {
    fetch('/api/config').then((r) => r.json()).then(setCfg).catch(() => setCfg(null))
  }, [])

  if (!cfg) return null
  return (
    <section className="section" id="environments" ref={ref}>
      <div className="wrap">
        <div className="section-head">
          <span className="eyebrow">Supported scenes</span>
          <h2>Eight environments, each with its own sound</h2>
          <p>Mappings live in one configuration file, so adding or retuning a scene never touches application code.</p>
        </div>
        <ul className={`env-grid${shown ? ' in' : ''}`}>
          {Object.entries(cfg.environments).map(([key, title], i) => (
            <li key={key} className="env-card" style={{ '--hue': HUE[key] ?? 340, '--i': i }}>
              <h3>{title}</h3>
              <ul className="env-sounds">
                {cfg.scene_sounds[key].map((r) => (
                  <li key={r.sound}>
                    <Icon name={soundIcon(r.sound)} size={16} />
                    <span>{cfg.sounds[r.sound].label}</span>
                    <i style={{ '--v': `${r.volume}%` }} aria-label={`${r.volume}% volume`} />
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
