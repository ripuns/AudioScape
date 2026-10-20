import WaveField from './WaveField.jsx'
import { Icon } from './icons.jsx'
import { useConfig } from '../api.js'

const FALLBACK = ['Beach', 'Forest', 'City', 'Cafe', 'Stadium', 'Mountain', 'Kitchen', 'Harbour']
const FEATURED = ['beach', 'forest', 'city', 'cafe', 'stadium', 'mountain', 'kitchen', 'harbour']

export default function Hero() {
  const cfg = useConfig()
  const envs = cfg?.environments
  const names = envs ? FEATURED.filter((k) => envs[k]).map((k) => envs[k]) : FALLBACK
  const more = envs ? Object.keys(envs).length - names.length : 0

  return (
    <section className="hero" id="top">
      <div className="hero-glow" aria-hidden="true" />
      <WaveField />
      <div className="wrap hero-in">
        <span className="eyebrow"><span className="dot" /> Image → Waveform → Audio</span>
        <h1>
          See a scene.<br />
          <span className="grad">Hear it.</span>
        </h1>
        <p className="lead">
          AudioScape reads the visual information in a photo, works out the environment and what is in it,
          and mixes a 30-second interactive soundscape: waves, wind, seagulls and footsteps for a beach,
          not just the label &ldquo;beach&rdquo;.
        </p>
        <div className="hero-cta">
          <a className="btn btn-lg" href="#studio"><Icon name="upload" size={18} /> Upload a photo</a>
          <a className="btn btn-lg btn-ghost" href="#environments">Browse scenes</a>
        </div>
        <ul className="scene-pills" aria-label="Supported environments">
          {names.map((s) => <li key={s}>{s}</li>)}
          {more > 0 && <li className="more"><a href="#environments">+{more} more</a></li>}
        </ul>
      </div>
    </section>
  )
}
