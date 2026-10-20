import { Icon } from './icons.jsx'

const STEPS = [
  ['Image upload', 'Decode, orient and resize'],
  ['Visual understanding', 'CLIP scene + tiled object scoring'],
  ['Sound mapping', 'Choose layers and volumes'],
  ['Audio mixing', 'Loop, place, mix and normalise'],
]

// stage: -1 idle, 0..3 step in progress, 4 all complete
export default function PipelineSteps({ stage }) {
  return (
    <div className="card pipeline">
      <div className="card-head"><h3>Pipeline</h3>
        <span className={`status ${stage === 4 ? 'ok' : stage >= 0 ? 'run' : ''}`}>
          {stage === 4 ? 'Complete' : stage >= 0 ? 'Working' : 'Idle'}
        </span>
      </div>
      <ol className="pipe">
        {STEPS.map(([t, s], i) => {
          const state = i < stage ? 'done' : i === stage ? 'active' : ''
          return (
            <li key={t} className={state}>
              <span className="node">
                {state === 'done' ? <Icon name="check" size={14} stroke={2.4} /> : state === 'active' ? <span className="spinner sm" /> : i + 1}
              </span>
              <div><strong>{t}</strong><span>{s}</span></div>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
