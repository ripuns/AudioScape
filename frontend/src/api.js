export async function createSoundscape(file) {
  const body = new FormData()
  body.append('image', file)
  const res = await fetch('/api/soundscape', { method: 'POST', body })
  if (!res.ok) {
    let detail = `Request failed (${res.status})`
    try { detail = (await res.json()).detail || detail } catch { /* keep default */ }
    throw new Error(detail)
  }
  return res.json()
}
