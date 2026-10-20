import { useEffect, useRef, useState } from 'react'
import { AudioEngine } from '../audioEngine.js'
import Waveform from './Waveform.jsx'
import Visualizer from './Visualizer.jsx'

const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`

export default function Player({ result }) {
  const engineRef = useRef(null)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState(null)
  const [playing, setPlaying] = useState(false)
  const [mode, setMode] = useState('mix')
  const [time, setTime] = useState(0)
  const [layers, setLayers] = useState(() =>
    Object.fromEntries(result.layers.map((l) => [l.sound, { level: 100, muted: false }])))

  useEffect(() => {
    const engine = new AudioEngine()
    engineRef.current = engine
    setReady(false); setError(null); setPlaying(false); setMode('mix')
    setLayers(Object.fromEntries(result.layers.map((l) => [l.sound, { level: 100, muted: false }])))
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
    }, 200)
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

  if (error) return <div className="error" role="alert">{error}</div>

  return (
    <div className="panel">
      <h2>Interactive Soundscape</h2>
      <div className="player-top" style={{ marginTop: 12 }}>
        <button onClick={toggle} disabled={!ready}>{playing ? 'Pause' : 'Play'}</button>
        <div className="modes" role="group" aria-label="Playback mode">
          <button className={mode === 'mix' ? 'on' : ''} onClick={() => changeMode('mix')} disabled={!ready}>Final mix</button>
          <button className={mode === 'layers' ? 'on' : ''} onClick={() => changeMode('layers')} disabled={!ready}>Layers</button>
        </div>
        <span className="time">{ready ? `${fmt(time)} / ${fmt(engine.duration)}` : 'Loading audio...'}</span>
        <a className="btn ghost" href={result.mix_url} download="audioscape-soundscape.wav">Download WAV</a>
      </div>

      {engine && <Waveform engine={engine} ready={ready} />}
      {engine && <Visualizer engine={engine} />}

      <div className="layers">
        {result.layers.map((l) => {
          const st = layers[l.sound]
          const off = mode !== 'layers'
          return (
            <div key={l.sound} className={`layer${st.muted || off ? ' off' : ''}`}>
              <input type="checkbox" checked={!st.muted} disabled={off || !ready}
                onChange={(e) => update(l.sound, { muted: !e.target.checked })} aria-label={`Enable ${l.label}`} />
              <div>
                {l.label}
                <small>{l.kind === 'ambient' ? 'looped' : `${l.repeats}x`} · mix volume {l.volume}% · {l.sources.join(', ')}</small>
              </div>
              <input type="range" min="0" max="200" value={st.level} disabled={off || !ready}
                onChange={(e) => update(l.sound, { level: Number(e.target.value) })} aria-label={`${l.label} level`} />
              <span className="time">{st.level}%</span>
            </div>
          )
        })}
      </div>
      {mode !== 'layers' && <p className="muted">Switch to Layers to mute or rebalance individual sounds.</p>}
    </div>
  )
}
