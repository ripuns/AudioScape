import { useEffect, useRef } from 'react'

// Live audio visualization: frequency bars with the time-domain waveform on top.
export default function Visualizer({ engine }) {
  const ref = useRef(null)

  useEffect(() => {
    const canvas = ref.current
    const an = engine.analyser
    const freq = new Uint8Array(an.frequencyBinCount)
    const wave = new Uint8Array(an.fftSize)
    const dpr = window.devicePixelRatio || 1
    let raf

    const draw = () => {
      const w = canvas.clientWidth, h = canvas.clientHeight
      if (canvas.width !== w * dpr) { canvas.width = w * dpr; canvas.height = h * dpr }
      const g = canvas.getContext('2d')
      g.setTransform(dpr, 0, 0, dpr, 0, 0)
      g.clearRect(0, 0, w, h)
      an.getByteFrequencyData(freq)
      an.getByteTimeDomainData(wave)

      const bars = 64
      const bw = w / bars
      const usable = Math.floor(freq.length * 0.5)   // skip the near-empty top of the spectrum
      for (let i = 0; i < bars; i++) {
        const v = freq[Math.floor((i / bars) * usable)] / 255
        g.fillStyle = `hsl(${345 - v * 25}, 90%, ${45 + v * 25}%)`
        g.fillRect(i * bw + 1, h - v * h, bw - 2, v * h)
      }
      g.beginPath()
      g.lineWidth = 2
      g.strokeStyle = '#ffffff'
      for (let i = 0; i < wave.length; i += 4) {
        const x = (i / wave.length) * w
        const y = (wave[i] / 255) * h
        i === 0 ? g.moveTo(x, y) : g.lineTo(x, y)
      }
      g.stroke()
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(raf)
  }, [engine])

  return <canvas ref={ref} className="viz" aria-label="Live audio visualization" />
}
