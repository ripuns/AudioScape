import { useEffect, useState } from 'react'

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

// Backend configuration (environments, groups, mappings), fetched once and shared.
let configPromise
export function useConfig() {
  const [cfg, setCfg] = useState(null)
  useEffect(() => {
    configPromise ??= fetch('/api/config').then((r) => (r.ok ? r.json() : null)).catch(() => null)
    let live = true
    configPromise.then((c) => { if (live) setCfg(c) })
    return () => { live = false }
  }, [])
  return cfg
}
