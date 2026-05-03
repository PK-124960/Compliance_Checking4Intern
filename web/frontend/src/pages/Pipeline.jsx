import { useState, useRef, useEffect } from 'react'
import { Play, Square, CheckCircle, Circle, Loader } from 'lucide-react'

const PIPELINE_STEPS = [
  { id: 'extract', label: 'PDF Extraction', desc: 'Parse PDFs into sentences' },
  { id: 'prefilter', label: 'Heuristic Pre-filter', desc: 'Filter non-rule content' },
  { id: 'classify', label: 'LLM Classification', desc: 'Classify with Mistral 7B' },
  { id: 'fol', label: 'FOL Formalization', desc: 'Convert to First-Order Logic' },
  { id: 'shacl_fol', label: 'SHACL Generation (FOL)', desc: 'Translate FOL → SHACL shapes' },
  { id: 'shacl_nl', label: 'SHACL Generation (NL)', desc: 'Direct NL fallback path' },
  { id: 'validate', label: 'SHACL Validation', desc: 'Run pyshacl against test data' },
  { id: 'report', label: 'Report Generation', desc: 'Compile final report' },
]

export default function Pipeline() {
  const [running, setRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState(-1)
  const [completedSteps, setCompletedSteps] = useState(new Set())
  const [logs, setLogs] = useState([])
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState(null)
  const logRef = useRef(null)
  const abortRef = useRef(null)

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [logs])

  const runPipeline = async () => {
    setRunning(true)
    setCurrentStep(0)
    setCompletedSteps(new Set())
    setLogs([])
    setSummary(null)
    setError(null)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const res = await fetch('/api/run-pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: 'ait' }),
        signal: controller.signal,
      })

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            handleEvent(event)
          } catch {}
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message)
        addLog('error', `Pipeline failed: ${err.message}`)
      }
    }

    setRunning(false)
  }

  const stopPipeline = () => {
    if (abortRef.current) {
      abortRef.current.abort()
      addLog('warn', 'Pipeline aborted by user')
    }
    setRunning(false)
  }

  const handleEvent = (event) => {
    switch (event.type) {
      case 'step_start':
        const stepIdx = PIPELINE_STEPS.findIndex(s => s.id === event.step)
        if (stepIdx >= 0) setCurrentStep(stepIdx)
        addLog('info', `>> ${event.label || event.step}`)
        break
      case 'step_done':
        setCompletedSteps(prev => new Set([...prev, event.step]))
        if (event.detail) addLog('success', `   ${event.detail}`)
        break
      case 'log':
        addLog(event.level || 'info', event.message)
        break
      case 'warning':
        addLog('warn', event.message)
        break
      case 'summary':
        setSummary(event.data)
        addLog('success', '═══ Pipeline Complete ═══')
        break
      case 'error':
        setError(event.message)
        addLog('error', event.message)
        break
    }
  }

  const addLog = (level, message) => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false })
    setLogs(prev => [...prev, { time, level, message }])
  }

  const getStepStatus = (idx) => {
    const step = PIPELINE_STEPS[idx]
    if (completedSteps.has(step.id)) return 'done'
    if (idx === currentStep && running) return 'active'
    return 'pending'
  }

  const logColors = {
    info: 'var(--text-primary)',
    success: 'var(--success)',
    warn: 'var(--warning)',
    error: 'var(--danger)',
  }

  return (
    <>
      <div className="page-header">
        <h2>Run Pipeline</h2>
        <p>Execute the full policy formalization pipeline on the AIT corpus</p>
      </div>

      <div className="grid-2">
        {/* Left: Steps + Controls */}
        <div className="flex flex-col gap-4">
          <div className="card">
            <div className="card-header">
              <span>Pipeline Steps</span>
              {!running ? (
                <button className="btn btn-primary btn-sm" onClick={runPipeline}>
                  <Play size={14} /> Run Pipeline
                </button>
              ) : (
                <button className="btn btn-danger btn-sm" onClick={stopPipeline}>
                  <Square size={14} /> Stop
                </button>
              )}
            </div>
            <div className="card-body">
              <div className="pipeline-steps">
                {PIPELINE_STEPS.map((step, i) => {
                  const status = getStepStatus(i)
                  return (
                    <div key={step.id} className={`pipeline-step-item ${status}`}>
                      <div className={`step-icon ${status}`}>
                        {status === 'done' ? <CheckCircle size={14} /> :
                         status === 'active' ? <Loader size={14} className="spinner" /> :
                         <Circle size={14} />}
                      </div>
                      <div>
                        <div className="step-label">{step.label}</div>
                        <div className="text-xs text-muted">{step.desc}</div>
                      </div>
                      {status === 'active' && (
                        <div className="step-detail">
                          <div className="spinner" />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Summary card */}
          {summary && (
            <div className="card">
              <div className="card-header">Pipeline Summary</div>
              <div className="card-body">
                <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                  <div className="stat-card">
                    <div className="stat-label">Sentences</div>
                    <div className="stat-value">{summary.sentences_extracted}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Rules</div>
                    <div className="stat-value">{summary.rules_classified}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">FOL ok/fail</div>
                    <div className="stat-value">{summary.fol_ok}/{summary.fol_failed}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Violations</div>
                    <div className="stat-value">{summary.violations}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right: Live log */}
        <div className="card" style={{ alignSelf: 'start', position: 'sticky', top: '20px' }}>
          <div className="card-header">
            <span>Live Output</span>
            <span className="text-xs text-muted">{logs.length} lines</span>
          </div>
          <div
            ref={logRef}
            className="card-body"
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.76rem',
              lineHeight: '1.7',
              maxHeight: '560px',
              overflowY: 'auto',
              background: '#0f172a',
              color: '#e2e8f0',
              padding: '16px',
              borderRadius: '0 0 var(--radius-md) var(--radius-md)',
            }}
          >
            {logs.length === 0 ? (
              <span style={{ opacity: 0.4 }}>Click "Run Pipeline" to start...</span>
            ) : logs.map((log, i) => (
              <div key={i} style={{ color: logColors[log.level] || '#e2e8f0' }}>
                <span style={{ opacity: 0.5 }}>[{log.time}]</span> {log.message}
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}
