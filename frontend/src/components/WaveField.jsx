import { useEffect, useRef } from 'react'

// Flowing layered sine ribbons (the deck's "image -> waveform" motif) as a hero backdrop.
export default function WaveField() {
  const ref = useRef(null)

  useEffect(() => {
    const canvas = ref.current
    const g = canvas.getContext('2d')
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    let raf, w = 0, h = 0

    const resize = () => {
      w = canvas.clientWidth; h = canvas.clientHeight
      canvas.width = w * dpr; canvas.height = h * dpr
      g.setTransform(dpr, 0, 0, dpr, 0, 0)
    }
    resize()
    window.addEventListener('resize', resize)

    const LINES = 22
    const draw = (t) => {
      g.clearRect(0, 0, w, h)
      for (let i = 0; i < LINES; i++) {
        const k = i / (LINES - 1)
        g.beginPath()
        for (let x = 0; x <= w; x += 6) {
          const nx = x / w
          const amp = (h * 0.16) * (0.35 + 0.65 * Math.sin(nx * Math.PI)) * (0.6 + 0.4 * Math.sin(t * 0.0004 + k * 3))
          const y = h * 0.58
            + Math.sin(nx * 5.2 + t * 0.00055 + k * 1.1) * amp
            + Math.sin(nx * 9.5 - t * 0.0007 + k * 2.3) * amp * 0.35
            + (k - 0.5) * h * 0.2
          x === 0 ? g.moveTo(x, y) : g.lineTo(x, y)
        }
        const grad = g.createLinearGradient(0, 0, w, 0)
        grad.addColorStop(0, `rgba(255,143,171,${0.04 + k * 0.1})`)
        grad.addColorStop(0.5, `rgba(255,${90 + k * 60},${110 - k * 40},${0.18 + k * 0.4})`)
        grad.addColorStop(1, `rgba(243,18,73,${0.05 + k * 0.1})`)
        g.strokeStyle = grad
        g.lineWidth = 1.1
        g.stroke()
      }
      if (!reduce) raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize) }
  }, [])

  return <canvas ref={ref} className="wavefield" aria-hidden="true" />
}
