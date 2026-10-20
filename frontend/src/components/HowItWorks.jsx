import { Icon } from './icons.jsx'
import { useReveal } from '../useReveal.js'

const STEPS = [
  { icon: 'upload', title: 'Image upload', text: 'Drop in any photo. Pillow normalises orientation, colour and size before analysis.' },
  { icon: 'eye', title: 'Visual understanding', text: 'CLIP classifies the whole scene, then scores overlapping tiles to find people, birds, cars and more, with no training data.' },
  { icon: 'sliders', title: 'Sound mapping', text: 'A central configuration turns the scene and detected objects into sound layers, each with its own volume.' },
  { icon: 'wave', title: 'Audio mixing', text: 'Ambient beds loop, effects repeat sparingly, and everything is normalised into a clip-free 30-second WAV.' },
]

export default function HowItWorks() {
  const [ref, shown] = useReveal()
  return (
    <section className="section" id="how" ref={ref}>
      <div className="wrap">
        <div className="section-head">
          <span className="eyebrow">The pipeline</span>
          <h2>From pixels to a soundscape in four steps</h2>
          <p>A multimedia system whose core is the integration of visual and auditory media, not AI alone.</p>
        </div>
        <ol className={`steps-grid${shown ? ' in' : ''}`}>
          {STEPS.map((s, i) => (
            <li key={s.title} className="step-card" style={{ '--i': i }}>
              <span className="step-no">0{i + 1}</span>
              <span className="step-icon"><Icon name={s.icon} size={22} /></span>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </li>
          ))}
        </ol>
        <div className="example-strip">
          <span className="chip-lg">Beach scene</span><Icon name="arrow" size={16} />
          <span className="chip-lg">Waves + Wind</span><span className="plus">+</span>
          <span className="chip-lg">Bird → Seagulls</span><span className="plus">+</span>
          <span className="chip-lg">Person → Footsteps</span><Icon name="arrow" size={16} />
          <span className="chip-lg accent">Mixed soundscape</span>
        </div>
      </div>
    </section>
  )
}
