import { useState } from 'react'
import { useConfig } from '../api.js'
import { Icon, soundIcon } from './icons.jsx'
import { useReveal } from '../useReveal.js'

// accent hue per environment for the card glow
const HUE = {
  beach: 28, forest: 140, classroom: 48, city: 215, cafe: 22, stadium: 350, park: 100, rainy_street: 230,
  mountain: 200, lake: 190, countryside: 85, market: 12, railway_station: 255, highway: 235,
  kitchen: 35, library: 30, office: 205, harbour: 205, worship: 45,
}

export default function Environments() {
  const cfg = useConfig()
  const [group, setGroup] = useState('All')
  const [ref, shown] = useReveal(0.1)

  if (!cfg) return null
  const total = Object.keys(cfg.environments).length
  const groups = cfg.groups || {}
  const keys = group === 'All' ? Object.keys(cfg.environments) : groups[group] || []

  return (
    <section className="section" id="environments" ref={ref}>
      <div className="wrap">
        <div className="section-head">
          <span className="eyebrow">Supported scenes</span>
          <h2>{total} environments, each with its own sound</h2>
          <p>Mappings live in one configuration file, so adding or retuning a scene never touches application code.</p>
        </div>

        {Object.keys(groups).length > 0 && (
          <div className="tabs" role="tablist" aria-label="Environment groups">
            {['All', ...Object.keys(groups)].map((g) => (
              <button key={g} role="tab" aria-selected={group === g} className={group === g ? 'on' : ''} onClick={() => setGroup(g)}>
                {g}<span>{g === 'All' ? total : groups[g].length}</span>
              </button>
            ))}
          </div>
        )}

        <ul className={`env-grid${shown ? ' in' : ''}`} key={group}>
          {keys.map((key, i) => (
            <li key={key} className="env-card" style={{ '--hue': HUE[key] ?? 340, '--i': i }}>
              <h3>{cfg.environments[key]}</h3>
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
