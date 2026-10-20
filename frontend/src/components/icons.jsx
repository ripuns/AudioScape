// Small stroke-icon set (24x24, currentColor) used across the UI.
const P = {
  upload: 'M12 16V4m0 0L7 9m5-5 5 5M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2',
  eye: 'M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Zm10 3a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
  sliders: 'M4 6h9m4 0h3M4 12h3m4 0h9M4 18h11m4 0h1M15 4v4M9 10v4M17 16v4',
  wave: 'M2 12c2.5-6 4.5-6 6 0s3.5 6 6 0 3.5-6 8 0',
  play: 'M7 4.5v15a1 1 0 0 0 1.5.86l12-7.5a1 1 0 0 0 0-1.72l-12-7.5A1 1 0 0 0 7 4.5Z',
  pause: 'M8 5v14M16 5v14',
  download: 'M12 4v12m0 0 5-5m-5 5-5-5M4 20h16',
  github: 'M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12 12 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21',
  arrow: 'M5 12h14m0 0-6-6m6 6-6 6',
  check: 'm5 12.5 4.5 4.5L19 7.5',
  wind: 'M3 8h11a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 16h8a2.5 2.5 0 1 1-2.5 2.5',
  bird: 'M16 7h.01M3.4 18H12a9 9 0 0 0 8.9-8.8c0-.9-.2-1.7-.6-2.5L19 4l-2.1 1.1A5.7 5.7 0 0 0 12 3a6 6 0 0 0-6 6c0 4-1.4 6-2.6 9Z M20 7l2 1',
  bug: 'M9 8a3 3 0 1 1 6 0v1H9V8Zm-4 4h4m6 0h4M5 7l3 2m11-2-3 2M5 18l3-2m11 2-3-2M12 9v11m-3-8a3 3 0 0 0-1 2.5V16a4 4 0 0 0 8 0v-1.5A3 3 0 0 0 15 12',
  car: 'M5 17h14M6 17v2m12-2v2M4 13l1.7-5a2 2 0 0 1 1.9-1.4h8.8a2 2 0 0 1 1.9 1.4L20 13v4H4v-4Zm3 1.5h.01M17 14.5h.01',
  people: 'M16 20v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 4 18.5V20m12.5-9a3 3 0 1 0 0-6M20 20v-1.5a3.5 3.5 0 0 0-2.5-3.35M10 11.5a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z',
  rain: 'M7 16a4.5 4.5 0 1 1 1.3-8.8A5.5 5.5 0 0 1 19 9.5a3.25 3.25 0 0 1-.5 6.5M8 19l-1 2m5-2-1 2m5-2-1 2',
  music: 'M9 18V6l11-2v12M9 18a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm11-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  tool: 'm14.7 6.3 3 3m-12 9.4 8.6-8.6a4 4 0 0 0 5.4-5.2l-2.6 2.6-2.2-.4-.4-2.2 2.6-2.6a4 4 0 0 0-5.2 5.4l-8.6 8.6a1.9 1.9 0 0 0 2.7 2.7Z',
  steps: 'M8 4c-1.7 0-3 2-3 5v3h6V9c0-3-1.3-5-3-5Zm0 11H5v1.5a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2V15M16 8c-1.7 0-3 2-3 5v3h6v-3c0-3-1.3-5-3-5Zm0 11h-3v1.5a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2V19',
  paw: 'M8.5 10a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5Zm7 0a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5ZM5 14a1.75 1.75 0 1 0 0-3.5A1.75 1.75 0 0 0 5 14Zm14 0a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5ZM12 12.5c-3 0-5 3-5 4.8 0 1.4 1.3 2 2.6 2 .9 0 1.6-.4 2.4-.4s1.5.4 2.4.4c1.3 0 2.6-.6 2.6-2 0-1.8-2-4.8-5-4.8Z',
  clock: 'M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  whistle: 'M3 11h9l3-3h4a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2h-1a6 6 0 1 1-12 0v-3m7.5 3.5h.01',
  cup: 'M5 8h12v6a5 5 0 0 1-5 5H10a5 5 0 0 1-5-5V8Zm12 1h1.5a2.5 2.5 0 0 1 0 5H17M8 3v2m3-2v2m3-2v2',
  umbrella: 'M12 3a9 9 0 0 0-9 9h18a9 9 0 0 0-9-9Zm0 9v6.5a2 2 0 0 0 4 0',
  mic: 'M12 15a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3Zm-6-3a6 6 0 0 0 12 0m-6 6v3',
  leaf: 'M5 19C5 10 10 5 20 4c0 10-5 15-14 15Zm0 0 8-8',
  book: 'M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5Zm2 14h13M8 7h7',
  keyboard: 'M3 7h18v10H3V7Zm3 3h.01M9 10h.01M12 10h.01M15 10h.01M18 10h.01M7 14h10',
  phone: 'M6 3h3l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 4 5a2 2 0 0 1 2-2Z',
  bell: 'M6 16v-5a6 6 0 1 1 12 0v5l2 2H4l2-2Zm4 4a2 2 0 0 0 4 0',
  sparkle: 'M12 3v4m0 10v4M3 12h4m10 0h4M6 6l2.5 2.5m7 7L18 18M18 6l-2.5 2.5m-7 7L6 18',
}

export function Icon({ name, size = 20, stroke = 1.7, className = '', style }) {
  return (
    <svg className={className} style={style} width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={P[name] || P.sparkle} />
    </svg>
  )
}

// Which icon represents which sound
const SOUND_ICON = {
  waves: 'wave', wind: 'wind', leaves: 'leaf', insects: 'bug', birds: 'bird', seagulls: 'bird',
  traffic: 'car', horns: 'car', construction: 'tool', crowd: 'people', chatter: 'people',
  cheering: 'people', children: 'people', classroom: 'people', rain: 'rain', umbrella: 'umbrella',
  cafe_music: 'music', drums: 'music', footsteps: 'steps', barking: 'paw', clock: 'clock',
  whistle: 'whistle', cups: 'cup', espresso: 'cup', chalk: 'tool',
  stream: 'wave', lapping: 'wave', frogs: 'paw', rooster: 'bird', cows: 'paw', train: 'car',
  station: 'people', market: 'people', highway: 'car', kitchen: 'cup', tap: 'rain', library: 'book',
  typing: 'keyboard', phone: 'phone', ship_horn: 'whistle', bells: 'bell', chant: 'music',
}
export const soundIcon = (id) => SOUND_ICON[id] || 'wave'

export function Logo({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <defs>
        <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#ff8fab" /><stop offset="1" stopColor="#f31249" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill="url(#lg)" />
      {[[7, 12, 8], [11.5, 8, 16], [16, 5, 22], [20.5, 9, 14], [25, 13, 6]].map(([x, y, h]) => (
        <rect key={x} x={x - 1.1} y={y + 3} width="2.2" height={h * 0.62} rx="1.1" fill="#1a0a10" opacity=".9" />
      ))}
    </svg>
  )
}
