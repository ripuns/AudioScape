import { useEffect, useState } from 'react'
import { createSoundscape } from './api.js'
import UploadPanel from './components/UploadPanel.jsx'
import PipelineSteps from './components/PipelineSteps.jsx'
import SceneResult from './components/SceneResult.jsx'

export default function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [busy, setBusy] = useState(false)
  const [stage, setStage] = useState(-1)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [resultImage, setResultImage] = useState(null)

  useEffect(() => () => previewUrl && URL.revokeObjectURL(previewUrl), [previewUrl])

  const pick = (f) => {
    setFile(f); setPreviewUrl(URL.createObjectURL(f))
    setResult(null); setError(null); setStage(-1)
  }

  const generate = async () => {
    setBusy(true); setError(null); setResult(null); setStage(0)
    // the backend runs the stages in one request; step through them for feedback
    const timers = [1, 2, 3].map((s, i) => setTimeout(() => setStage(s), 400 + i * 1800))
    try {
      const r = await createSoundscape(file)
      setResult(r); setResultImage(previewUrl); setStage(4)
    } catch (e) {
      setError(e.message); setStage(-1)
    } finally {
      timers.forEach(clearTimeout); setBusy(false)
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <h1>AudioScape</h1>
        <div className="tagline">Image → Waveform → Audio</div>
        <p>Transforming visual scenes into interactive soundscapes.</p>
      </header>

      <section><PipelineSteps stage={stage} /></section>
      <section>
        <UploadPanel file={file} previewUrl={previewUrl} busy={busy} onPick={pick} onGenerate={generate} />
        {error && <div className="error" role="alert">{error}</div>}
      </section>
      {result && <section><SceneResult result={result} imageUrl={resultImage} /></section>}
    </div>
  )
}
