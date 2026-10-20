import { Logo } from './icons.jsx'

const TEAM = [['Ripun Sethia', '23BIT0421'], ['Yash Joshi', '23BIT0137'], ['Lakshya Gupta', '23BIT0103']]
const STACK = ['React', 'Vite', 'Web Audio API', 'FastAPI', 'CLIP', 'Pillow', 'pydub', 'FFmpeg']

export default function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer-in">
        <div className="footer-brand">
          <a className="brand" href="#top"><Logo size={26} /><span>AudioScape</span></a>
          <p>Transforming visual scenes into interactive soundscapes.</p>
        </div>
        <div>
          <h4>Team</h4>
          <ul>{TEAM.map(([n, id]) => <li key={id}>{n} <span>{id}</span></li>)}</ul>
        </div>
        <div>
          <h4>Built with</h4>
          <ul className="stack">{STACK.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
      </div>
      <div className="wrap footer-base">
        <span>Sound recordings from Wikimedia Commons under CC0, public domain, CC BY and CC BY-SA licences.</span>
        <a href="https://github.com/ripuns/AudioScape" target="_blank" rel="noreferrer">Source &amp; credits</a>
      </div>
    </footer>
  )
}
