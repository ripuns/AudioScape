import { useEffect, useRef, useState } from 'react'
import { createSoundscape } from '../api.js'
import UploadPanel from './UploadPanel.jsx'
import PipelineSteps from './PipelineSteps.jsx'
import SceneResult from './SceneResult.jsx'
import Player from './Player.jsx'

export default function Studio() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [busy, setBusy] = useState(false)
  const [stage, setStage] = useState(-1)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [resultImage, setResultImage] = useState(null)
  const resultRef = useRef(null)

  useEffect(() => () => previewUrl && URL.revokeObjectURL(previewUrl), [previewUrl])

  const pick = (f) => {
    setFile(f); setPreviewUrl(URL.createObjectURL(f))
    setResult(null); setError(null); setStage(-1)
  }
  const clear = () => { setFile(null); setPreviewUrl(null); setResult(null); setError(null); setStage(-1) }

  const generate = async () => {
    setBusy(true); setError(null); setResult(null); setStage(0)
    // The backend runs all stages in one request; step through them for feedback.
    const timers = [1, 2, 3].map((s, i) => setTimeout(() => setStage(s), 500 + i * 1700))
    try {
      const r = await createSoundscape(file)
      setResult(r); setResultImage(previewUrl); setStage(4)
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 150)
    } catch (e) {
      setError(e.message === 'Failed to fetch' ? 'Could not reach the AudioScape server. Is the backend running on port 8000?' : e.message)
      setStage(-1)
    } finally {
      timers.forEach(clearTimeout); setBusy(false)
    }
  }

  return (
    <section className="section studio" id="studio">
      <div className="wrap">
        <div className="section-head">
          <span className="eyebrow">Studio</span>
          <h2>Turn your photo into sound</h2>
          <p>Upload an image and AudioScape will analyse it, pick the sounds and mix them for you.</p>
        </div>
        <div className="studio-grid">
          <UploadPanel file={file} previewUrl={previewUrl} busy={busy} onPick={pick} onClear={clear} onGenerate={generate} />
          <PipelineSteps stage={stage} />
        </div>
        {error && <div className="toast error" role="alert">{error}</div>}
        {result && (
          <div className="results" ref={resultRef}>
            <SceneResult result={result} imageUrl={resultImage} />
            <Player key={result.id} result={result} />
          </div>
        )}
      </div>
    </section>
  )
}
