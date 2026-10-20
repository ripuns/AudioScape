import WaveField from './WaveField.jsx'
import { Icon } from './icons.jsx'

const SCENES = ['Beach', 'Forest', 'Classroom', 'City', 'Cafe', 'Stadium', 'Park', 'Rainy Street']

export default function Hero() {
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
          <a className="btn btn-lg btn-ghost" href="#how">How it works</a>
        </div>
        <ul className="scene-pills" aria-label="Supported environments">
          {SCENES.map((s) => <li key={s}>{s}</li>)}
        </ul>
      </div>
    </section>
  )
}
