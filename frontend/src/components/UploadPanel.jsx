import { useRef, useState } from 'react'

export default function UploadPanel({ file, previewUrl, busy, onPick, onGenerate }) {
  const input = useRef(null)
  const [over, setOver] = useState(false)

  const take = (f) => { if (f && f.type.startsWith('image/')) onPick(f) }

  return (
    <div className="panel">
      <h2>Image Upload</h2>
      <div
        className={`drop${over ? ' over' : ''}`}
        style={{ marginTop: 12 }}
        onClick={() => input.current.click()}
        onDragOver={(e) => { e.preventDefault(); setOver(true) }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); take(e.dataTransfer.files[0]) }}
      >
        {previewUrl
          ? <img src={previewUrl} alt="Selected scene" />
          : <span>Drop a photo here or click to browse<br /><small>Beach, forest, city, cafe, stadium...</small></span>}
        <input ref={input} type="file" accept="image/*" hidden onChange={(e) => take(e.target.files[0])} />
      </div>
      <div style={{ marginTop: 14 }}>
        <button disabled={!file || busy} onClick={onGenerate}>
          {busy ? 'Generating...' : 'Generate soundscape'}
        </button>
      </div>
    </div>
  )
}
