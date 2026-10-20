import { Icon } from './icons.jsx'

const pct = (v) => `${Math.round(v * 100)}%`
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1)

function Ring({ value }) {
  const r = 52, c = 2 * Math.PI * r
  return (
    <svg className="ring" viewBox="0 0 120 120" role="img" aria-label={`Confidence ${pct(value)}`}>
      <defs>
        <linearGradient id="ringg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#ff8fab" /><stop offset="1" stopColor="#f31249" />
        </linearGradient>
      </defs>
      <circle cx="60" cy="60" r={r} className="ring-bg" />
      <circle cx="60" cy="60" r={r} className="ring-fg" strokeDasharray={`${c * value} ${c}`} transform="rotate(-90 60 60)" />
      <text x="60" y="58" textAnchor="middle" className="ring-n">{Math.round(value * 100)}</text>
      <text x="60" y="76" textAnchor="middle" className="ring-u">% match</text>
    </svg>
  )
}

export default function SceneResult({ result, imageUrl }) {
  const { scene, objects } = result
  const ranked = Object.entries(scene.scores).slice(0, 5)
  return (
    <div className="result-grid">
      <div className="card">
        <div className="card-head"><h3>Detected regions</h3><span className="muted">Tiled CLIP scoring</span></div>
        <div className="stage">
          <img src={imageUrl} alt="Analysed scene" />
          {objects.map((o, i) => (
            <div key={i} className="box" style={{ left: `${o.box.x * 100}%`, top: `${o.box.y * 100}%`,
              width: `${o.box.w * 100}%`, height: `${o.box.h * 100}%` }}>
              <span>{cap(o.label)} {pct(o.score)}</span>
            </div>
          ))}
        </div>
        <p className="foot-note"><Icon name="eye" size={15} /> Boxes are coarse tile regions, not precise object detection.</p>
      </div>

      <div className="card">
        <div className="card-head"><h3>Scene classification</h3><span className="muted">Whole image</span></div>
        <div className="scene-top">
          <Ring value={scene.confidence} />
          <div>
            <span className="eyebrow sm">Dominant environment</span>
            <div className="scene-name">{scene.label}</div>
            <p className="muted">Sets the ambience: {result.layers.filter((l) => l.sources.some((s) => s.startsWith('scene'))).length} base layers.</p>
          </div>
        </div>
        <ul className="bars">
          {ranked.map(([name, v]) => (
            <li key={name} className={name === scene.label ? 'top' : ''}>
              <span>{name}</span>
              <div className="track"><div className="fill" style={{ width: pct(v) }} /></div>
              <span className="num">{pct(v)}</span>
            </li>
          ))}
        </ul>
        <div className="divider" />
        <div className="card-head"><h3>Objects found</h3></div>
        {objects.length === 0
          ? <p className="muted">Nothing above the detection threshold, so the soundscape follows the scene alone.</p>
          : <div className="chips">{objects.map((o, i) => (
              <span className="chip" key={i}>{cap(o.label)}<b>{pct(o.score)}</b></span>
            ))}</div>}
      </div>
    </div>
  )
}
