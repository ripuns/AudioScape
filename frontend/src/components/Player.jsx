import { useEffect, useRef, useState } from 'react'
import { AudioEngine } from '../audioEngine.js'
import Waveform from './Waveform.jsx'
import Visualizer from './Visualizer.jsx'
import { Icon, soundIcon } from './icons.jsx'

const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`
const initial = (layers) => Object.fromEntries(layers.map((l) => [l.sound, { level: 100, muted: false }]))

export default function Player({ result }) {
  const engineRef = useRef(null)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState(null)
  const [playing, setPlaying] = useState(false)
  const [mode, setMode] = useState('mix')
  const [time, setTime] = useState(0)
  const [layers, setLayers] = useState(() => initial(result.layers))

  useEffect(() => {
    const engine = new AudioEngine()
    engineRef.current = engine
    let cancelled = false
    engine.load(result.mix_url, result.layers)
      .then(() => { if (!cancelled) setReady(true) })
      .catch((e) => { if (!cancelled) setError(e.message) })
    return () => { cancelled = true; engine.dispose() }
  }, [result])

  useEffect(() => {
    const id = setInterval(() => {
      const e = engineRef.current
      if (e && ready) setTime(e.position)
    }, 120)
    return () => clearInterval(id)
  }, [ready])

  const engine = engineRef.current
  const toggle = async () => {
    if (engine.playing) { engine.pause(); setPlaying(false) } else { await engine.play(); setPlaying(true) }
  }
  const changeMode = (m) => { engine.setMode(m); setMode(m) }
  const update = (id, patch) => {
    setLayers((prev) => ({ ...prev, [id]: { ...prev[id], ...patch } }))
    if ('level' in patch) engine.setLayerLevel(id, patch.level / 100)
    if ('muted' in patch) engine.setLayerMuted(id, patch.muted)
  }

  if (error) return <div className="toast error" role="alert">{error}</div>
  const duration = ready ? engine.duration : result.duration_ms / 1000
  const off = mode !== 'layers'

  return (
    <div className="card player">
      <div className="player-bar">
        <button className={`play${playing ? ' on' : ''}`} onClick={toggle} disabled={!ready}
          aria-label={playing ? 'Pause' : 'Play'}>
          {ready ? <Icon name={playing ? 'pause' : 'play'} size={26} stroke={playing ? 2.6 : 1.5} style={playing ? undefined : { fill: 'currentColor' }} />
            : <span className="spinner" />}
        </button>
        <div className="player-title">
          <span className="eyebrow sm">Interactive soundscape</span>
          <strong>{result.scene.label} &middot; {result.layers.length} layers</strong>
          <span className="time">{fmt(time)} <i>/</i> {fmt(duration)}</span>
        </div>
        <div className="player-actions">
          <div className="seg" role="group" aria-label="Playback mode">
            <button className={mode === 'mix' ? 'on' : ''} onClick={() => changeMode('mix')} disabled={!ready}>Final mix</button>
            <button className={mode === 'layers' ? 'on' : ''} onClick={() => changeMode('layers')} disabled={!ready}>Layers</button>
          </div>
          <a className="btn btn-ghost btn-sm" href={result.mix_url} download="audioscape-soundscape.wav">
            <Icon name="download" size={16} /> WAV
          </a>
        </div>
      </div>

      {engine && <Waveform engine={engine} ready={ready} />}
      {engine && <Visualizer engine={engine} />}

      <div className="mixer-head">
        <h3>Sound layers</h3>
        <span className="muted">{off ? 'Switch to Layers mode to mute or rebalance each sound' : 'Mute or rebalance each sound live'}</span>
      </div>
      <ul className={`layers${off ? ' locked' : ''}`}>
        {result.layers.map((l) => {
          const st = layers[l.sound]
          const fromObject = l.sources.some((s) => s.startsWith('object'))
          return (
            <li key={l.sound} className={`layer${st.muted ? ' muted' : ''}`}>
              <div className="layer-top">
                <span className="layer-icon"><Icon name={soundIcon(l.sound)} size={18} /></span>
                <div className="layer-name">
                  <strong>{l.label}</strong>
                  <span>{l.kind === 'ambient' ? 'Looped bed' : `Effect ×${l.repeats}`}{fromObject ? ' · from object' : ''}</span>
                </div>
                <button className={`switch${st.muted ? '' : ' on'}`} role="switch" aria-checked={!st.muted}
                  aria-label={`${st.muted ? 'Unmute' : 'Mute'} ${l.label}`} disabled={off || !ready}
                  onClick={() => update(l.sound, { muted: !st.muted })}><i /></button>
              </div>
              <div className="layer-ctl">
                <input type="range" min="0" max="200" value={st.level} disabled={off || !ready}
                  style={{ '--p': `${st.level / 2}%` }} aria-label={`${l.label} level`}
                  onChange={(e) => update(l.sound, { level: Number(e.target.value) })} />
                <span className="num">{st.level}%</span>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
