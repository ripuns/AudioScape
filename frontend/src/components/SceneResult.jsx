const pct = (v) => `${Math.round(v * 100)}%`
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1)

export default function SceneResult({ result, imageUrl }) {
  const { scene, objects } = result
  return (
    <div className="grid">
      <div className="panel">
        <h2>Visual Understanding</h2>
        <div className="stage" style={{ marginTop: 12 }}>
          <img src={imageUrl} alt="Analysed scene" />
          {objects.map((o, i) => (
            <div key={i} className="box" title={`${o.label} ${pct(o.score)}`}
              style={{ left: `${o.box.x * 100}%`, top: `${o.box.y * 100}%`,
                       width: `${o.box.w * 100}%`, height: `${o.box.h * 100}%` }}>
              <span>{cap(o.label)} {pct(o.score)}</span>
            </div>
          ))}
        </div>
        <p className="muted">Boxes are coarse tile regions from CLIP, not precise object detection.</p>
      </div>
      <div className="panel">
        <h3>Scene classification</h3>
        <div className="big">{scene.label} - {pct(scene.confidence)}</div>
        <ul className="bars">
          {Object.entries(scene.scores).map(([name, v]) => (
            <li key={name} className={name === scene.label ? 'top' : ''}>
              <span>{name}</span>
              <div className="track"><div className="fill" style={{ width: pct(v) }} /></div>
              <span>{pct(v)}</span>
            </li>
          ))}
        </ul>
        <h3 style={{ marginTop: 20 }}>Tiled object detection</h3>
        {objects.length === 0
          ? <p className="muted">No objects above the detection threshold.</p>
          : <div className="chips">{objects.map((o, i) =>
              <span className="chip" key={i}>{cap(o.label)} - {pct(o.score)}</span>)}</div>}
      </div>
    </div>
  )
}
