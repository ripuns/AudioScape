// Web Audio engine: plays either the final normalized mix or the individual layer stems
// (which sum to the mix) with per-layer gain/mute. An AnalyserNode feeds the visualizer.
export class AudioEngine {
  constructor() {
    this.ctx = new (window.AudioContext || window.webkitAudioContext)()
    this.master = this.ctx.createGain()
    this.analyser = this.ctx.createAnalyser()
    this.analyser.fftSize = 2048
    this.analyser.smoothingTimeConstant = 0.8
    this.master.connect(this.analyser)
    this.analyser.connect(this.ctx.destination)

    this.mixBuffer = null
    this.stems = new Map()       // sound id -> { buffer, gain: GainNode, level, muted }
    this.mode = 'mix'            // 'mix' | 'layers'
    this.playing = false
    this.offset = 0              // seconds into the soundscape when paused
    this.startedAt = 0
    this.sources = []
  }

  async load(mixUrl, layers) {
    const decode = async (url) => {
      const res = await fetch(url)
      if (!res.ok) throw new Error(`Could not load audio (${res.status})`)
      return this.ctx.decodeAudioData(await res.arrayBuffer())
    }
    const [mix, ...bufs] = await Promise.all([decode(mixUrl), ...layers.map((l) => decode(l.url))])
    this.mixBuffer = mix
    layers.forEach((l, i) => {
      const gain = this.ctx.createGain()
      gain.connect(this.master)
      this.stems.set(l.sound, { buffer: bufs[i], gain, level: 1, muted: false })
    })
  }

  get duration() { return this.mixBuffer ? this.mixBuffer.duration : 0 }

  get position() {
    if (!this.playing) return this.offset
    return (this.ctx.currentTime - this.startedAt) % this.duration
  }

  _start() {
    const make = (buffer, dest) => {
      const src = this.ctx.createBufferSource()
      src.buffer = buffer
      src.loop = true
      src.connect(dest)
      src.start(0, this.offset)
      return src
    }
    if (this.mode === 'mix') {
      this.sources = [make(this.mixBuffer, this.master)]
    } else {
      this.sources = [...this.stems.values()].map((s) => make(s.buffer, s.gain))
    }
    this.startedAt = this.ctx.currentTime - this.offset
    this.playing = true
  }

  _stop() {
    this.sources.forEach((s) => { try { s.stop() } catch { /* already stopped */ } })
    this.sources = []
  }

  async play() {
    if (this.playing || !this.mixBuffer) return
    await this.ctx.resume()
    this._start()
  }

  pause() {
    if (!this.playing) return
    this.offset = this.position
    this._stop()
    this.playing = false
  }

  seek(seconds) {
    const wasPlaying = this.playing
    if (wasPlaying) { this._stop(); this.playing = false }
    this.offset = Math.min(Math.max(seconds, 0), this.duration - 0.001)
    if (wasPlaying) this._start()
  }

  setMode(mode) {
    if (mode === this.mode) return
    const wasPlaying = this.playing
    if (wasPlaying) this.pause()
    this.mode = mode
    if (wasPlaying) this.play()
  }

  _applyGain(s) { s.gain.gain.value = s.muted ? 0 : s.level }

  setLayerLevel(id, level) {
    const s = this.stems.get(id)
    if (s) { s.level = level; this._applyGain(s) }
  }

  setLayerMuted(id, muted) {
    const s = this.stems.get(id)
    if (s) { s.muted = muted; this._applyGain(s) }
  }

  dispose() {
    this._stop()
    this.playing = false
    this.ctx.close()
  }
}

// Peak envelope (min/max per bucket) of a buffer's first channel, for the waveform view.
export function peaks(buffer, buckets) {
  const data = buffer.getChannelData(0)
  const size = Math.floor(data.length / buckets)
  const out = new Float32Array(buckets)
  for (let i = 0; i < buckets; i++) {
    let max = 0
    for (let j = i * size; j < (i + 1) * size; j++) max = Math.max(max, Math.abs(data[j]))
    out[i] = max
  }
  return out
}
