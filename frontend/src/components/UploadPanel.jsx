import { useRef, useState } from 'react'
import { Icon } from './icons.jsx'

const size = (b) => (b > 1e6 ? `${(b / 1e6).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1e3))} KB`)

export default function UploadPanel({ file, previewUrl, busy, onPick, onClear, onGenerate }) {
  const input = useRef(null)
  const [over, setOver] = useState(false)
  const [warn, setWarn] = useState(null)

  const take = (f) => {
    if (!f) return
    if (!f.type.startsWith('image/')) return setWarn('Please choose an image file (JPG, PNG, WebP).')
    if (f.size > 15 * 1024 * 1024) return setWarn('That image is over 15 MB. Try a smaller one.')
    setWarn(null)
    onPick(f)
  }

  return (
    <div className="card upload">
      <div className="card-head">
        <h3>Your scene</h3>
        {file && !busy && <button className="link" onClick={onClear}>Remove</button>}
      </div>

      <div
        className={`drop${over ? ' over' : ''}${previewUrl ? ' has' : ''}`}
        role="button" tabIndex={0}
        aria-label="Choose or drop an image"
        onClick={() => !busy && input.current.click()}
        onKeyDown={(e) => { if ((e.key === 'Enter' || e.key === ' ') && !busy) { e.preventDefault(); input.current.click() } }}
        onDragOver={(e) => { e.preventDefault(); setOver(true) }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); !busy && take(e.dataTransfer.files[0]) }}
      >
        {previewUrl ? (
          <>
            <img src={previewUrl} alt="Selected scene" />
            {busy && <div className="scan" aria-hidden="true" />}
          </>
        ) : (
          <div className="drop-empty">
            <span className="drop-icon"><Icon name="upload" size={26} /></span>
            <strong>Drop a photo here</strong>
            <span>or click to browse &middot; JPG, PNG, WebP up to 15 MB</span>
          </div>
        )}
        <input ref={input} type="file" accept="image/*" hidden onChange={(e) => { take(e.target.files[0]); e.target.value = '' }} />
      </div>

      {warn && <p className="warn" role="alert">{warn}</p>}
      {file && <p className="file-meta"><span>{file.name}</span><span>{size(file.size)}</span></p>}

      <button className="btn btn-lg btn-block" disabled={!file || busy} onClick={onGenerate}>
        {busy ? <><span className="spinner" /> Generating soundscape</> : <><Icon name="sparkle" size={18} /> Generate soundscape</>}
      </button>
    </div>
  )
}
