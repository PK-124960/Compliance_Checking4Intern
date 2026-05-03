import { useState, useEffect } from 'react'
import { Database, ShieldCheck, AlertTriangle, CheckCircle, Loader } from 'lucide-react'
import Badge from '../components/Badge'

export default function Validate() {
  const [dbStatus, setDbStatus] = useState(null)
  const [entities, setEntities] = useState([])
  const [selectedEntities, setSelectedEntities] = useState(new Set())
  const [turtleData, setTurtleData] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingDb, setLoadingDb] = useState(false)
  const [validating, setValidating] = useState(false)

  // Check DB status on mount
  useEffect(() => {
    fetch('/api/db-status')
      .then(r => r.json())
      .then(data => setDbStatus(data))
      .catch(() => setDbStatus({ ok: false, error: 'Cannot reach API' }))
  }, [])

  // Load entity list
  useEffect(() => {
    if (dbStatus?.ok) {
      fetch('/api/db-entities')
        .then(r => r.json())
        .then(data => setEntities(data.entities || []))
        .catch(() => {})
    }
  }, [dbStatus])

  const toggleEntity = (name) => {
    setSelectedEntities(prev => {
      const next = new Set(prev)
      next.has(name) ? next.delete(name) : next.add(name)
      return next
    })
  }

  const selectAll = () => {
    if (selectedEntities.size === entities.length) {
      setSelectedEntities(new Set())
    } else {
      setSelectedEntities(new Set(entities.map(e => e.name)))
    }
  }

  const loadFromDb = async () => {
    setLoadingDb(true)
    try {
      const body = selectedEntities.size > 0
        ? { entities: [...selectedEntities] }
        : { entities: 'all' }
      const res = await fetch('/api/load-from-db', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (data.turtle) {
        setTurtleData(data.turtle)
      }
    } catch (err) {
      console.error('Failed to load from DB:', err)
    }
    setLoadingDb(false)
  }

  const runValidation = async () => {
    if (!turtleData.trim()) return
    setValidating(true)
    setResults(null)
    try {
      const res = await fetch('/api/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: turtleData, shapes: 'all' }),
      })
      const data = await res.json()
      setResults(data)
    } catch (err) {
      setResults({ error: err.message })
    }
    setValidating(false)
  }

  // Group violations by entity
  const groupedViolations = results?.violations?.reduce((acc, v) => {
    const key = v.focus_node || 'Unknown'
    if (!acc[key]) acc[key] = []
    acc[key].push(v)
    return acc
  }, {}) || {}

  return (
    <>
      <div className="page-header">
        <h2>Compliance Validator</h2>
        <p>Load entities from the database, convert to RDF, and validate against generated SHACL shapes</p>
      </div>

      {/* DB Status */}
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <div className="stat-card">
          <div className="stat-label">Database</div>
          <div className="stat-value" style={{ fontSize: '1rem', color: dbStatus?.ok ? 'var(--success)' : 'var(--danger)' }}>
            {dbStatus?.ok ? '● Connected' : '● Disconnected'}
          </div>
          <div className="stat-sub">{dbStatus?.ok ? 'PostgreSQL ready' : dbStatus?.error || 'Loading...'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Entities</div>
          <div className="stat-value">{entities.length}</div>
          <div className="stat-sub">{selectedEntities.size} selected</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Validation</div>
          <div className="stat-value" style={{ fontSize: '1rem' }}>
            {results ? (results.conforms ? '✓ Conforms' : `${results.total_violations} violations`) : '—'}
          </div>
          <div className="stat-sub">{results ? `${results.total_entities} entities checked` : 'Not run yet'}</div>
        </div>
      </div>

      <div className="grid-2">
        {/* Left: Entity selection + RDF */}
        <div className="flex flex-col gap-4">
          {/* Entity selector */}
          <div className="card">
            <div className="card-header">
              <span><Database size={16} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} />Entity Selector</span>
              <div className="flex gap-2">
                <button className="btn btn-outline btn-sm" onClick={selectAll}>
                  {selectedEntities.size === entities.length ? 'Deselect All' : 'Select All'}
                </button>
                <button
                  className="btn btn-primary btn-sm"
                  onClick={loadFromDb}
                  disabled={loadingDb || !dbStatus?.ok}
                >
                  {loadingDb ? <><Loader size={14} className="spinner" /> Loading...</> : 'Load from DB'}
                </button>
              </div>
            </div>
            <div className="card-body">
              {!dbStatus?.ok ? (
                <p className="text-muted text-sm">Database not connected. Start PostgreSQL to load entities.</p>
              ) : entities.length === 0 ? (
                <p className="text-muted text-sm">No entities found. Run <code>python -m db.seed</code> to populate.</p>
              ) : (
                <div className="entity-list">
                  {entities.map(entity => (
                    <label
                      key={entity.name}
                      className={`entity-item ${selectedEntities.has(entity.name) ? 'selected' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedEntities.has(entity.name)}
                        onChange={() => toggleEntity(entity.name)}
                      />
                      <div>
                        <div style={{ fontWeight: 600 }}>{entity.name}</div>
                        <div className="entity-type">{entity.type} · {entity.properties} properties</div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* RDF Preview */}
          <div className="card">
            <div className="card-header">
              <span>RDF Data (Turtle)</span>
              <span className="text-xs text-muted">{turtleData ? `${turtleData.split('\n').length} lines` : 'Empty'}</span>
            </div>
            <div className="card-body">
              <textarea
                className="input"
                value={turtleData}
                onChange={e => setTurtleData(e.target.value)}
                placeholder="Load from database or paste RDF Turtle data here..."
                style={{ minHeight: '220px' }}
              />
              <div className="mt-3 flex gap-2">
                <button
                  className="btn btn-primary"
                  onClick={runValidation}
                  disabled={validating || !turtleData.trim()}
                >
                  {validating ? <><div className="spinner" /> Validating...</> : <><ShieldCheck size={16} /> Run Validation</>}
                </button>
                {turtleData && (
                  <button className="btn btn-outline" onClick={() => { setTurtleData(''); setResults(null) }}>
                    Clear
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Results */}
        <div className="flex flex-col gap-4">
          <div className="card">
            <div className="card-header">
              <span>Validation Results</span>
              {results && (
                <Badge type={results.conforms ? 'success' : 'violation'}>
                  {results.conforms ? 'CONFORMS' : 'NON-CONFORMANT'}
                </Badge>
              )}
            </div>
            <div className="card-body">
              {!results ? (
                <div className="text-center text-muted" style={{ padding: '60px 20px' }}>
                  <ShieldCheck size={48} style={{ opacity: 0.2, marginBottom: '12px' }} />
                  <p>Load entities and run validation to see results</p>
                </div>
              ) : results.error ? (
                <div style={{ color: 'var(--danger)', padding: '20px' }}>
                  <AlertTriangle size={20} /> Error: {results.error}
                </div>
              ) : results.conforms ? (
                <div className="conforms-true" style={{ padding: '40px', textAlign: 'center' }}>
                  <CheckCircle size={40} style={{ marginBottom: '12px' }} />
                  <div style={{ fontSize: '1.1rem' }}>All entities conform to policy rules</div>
                  <div className="text-xs mt-2">{results.total_entities} entities validated</div>
                </div>
              ) : (
                <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                  <div className="mb-3 text-sm text-muted">
                    {results.total_violations} violations across {Object.keys(groupedViolations).length} entities
                  </div>
                  {Object.entries(groupedViolations).map(([entity, violations]) => (
                    <div key={entity} style={{ marginBottom: '16px' }}>
                      <div style={{ fontWeight: 700, fontSize: '0.87rem', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>{entity}</span>
                        <span className="badge badge-violation">{violations.length}</span>
                      </div>
                      {violations.slice(0, 8).map((v, i) => (
                        <div key={i} className={`result-card ${v.severity === 'Info' ? 'severity-info' : ''}`}>
                          <div className="result-shape">{v.source_shape}</div>
                          {v.path && <div className="result-path">sh:path {v.path}</div>}
                          {v.message && (
                            <div className="text-xs text-muted mt-2" style={{ lineHeight: '1.5' }}>
                              {v.message.slice(0, 200)}
                            </div>
                          )}
                        </div>
                      ))}
                      {violations.length > 8 && (
                        <div className="text-xs text-muted" style={{ paddingLeft: '18px' }}>
                          + {violations.length - 8} more violations...
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
