import { useEffect, useRef } from 'react'
import { peaks } from '../audioEngine.js'

// Static waveform of the final mix with a moving playhead; click to seek.
export default function Waveform({ engine, ready }) {
  const ref = useRef(null)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas || !ready) return
    const dpr = window.devicePixelRatio || 1
    let raf, p, cachedW = 0

    const draw = () => {
      const w = canvas.clientWidth, h = canvas.clientHeight
      if (canvas.width !== w * dpr) { canvas.width = w * dpr; canvas.height = h * dpr }
      if (w !== cachedW) { p = peaks(engine.mixBuffer, Math.max(Math.floor(w / 3), 1)); cachedW = w }
      const g = canvas.getContext('2d')
      g.setTransform(dpr, 0, 0, dpr, 0, 0)
      g.clearRect(0, 0, w, h)
      const played = engine.position / engine.duration
      const bw = w / p.length
      for (let i = 0; i < p.length; i++) {
        g.fillStyle = i / p.length < played ? '#f31249' : '#ff8fab'
        const bh = Math.max(p[i] * h * 0.95, 1)
        g.fillRect(i * bw, (h - bh) / 2, Math.max(bw - 1, 1), bh)
      }
      g.fillStyle = '#fff'
      g.fillRect(played * w, 0, 2, h)
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(raf)
  }, [engine, ready])

  const seek = (e) => {
    const r = e.currentTarget.getBoundingClientRect()
    engine.seek(((e.clientX - r.left) / r.width) * engine.duration)
  }

  return <canvas ref={ref} className="wave" onClick={seek} aria-label="Soundscape waveform; click to seek" />
}
