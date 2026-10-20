const STEPS = ['Image Upload', 'Visual Understanding', 'Sound Mapping', 'Audio Mixing']

// stage: -1 idle, 0..3 the step in progress, 4 all complete
export default function PipelineSteps({ stage }) {
  return (
    <ol className="steps" aria-label="Pipeline">
      {STEPS.map((s, i) => (
        <li key={s} className={i < stage ? 'done' : i === stage ? 'active' : ''}>{s}</li>
      ))}
    </ol>
  )
}
