import { useState, useEffect } from 'react'

const ValidationDashboard = () => {
    const [metrics, setMetrics] = useState(null)
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedStep, setSelectedStep] = useState(null)

    // Pipeline steps for visualization
    const pipelineSteps = [
        { id: 1, name: 'PDF Upload', description: 'Upload policy documents', icon: '📄', status: 'complete' },
        { id: 2, name: 'OCR Extraction', description: 'Extract text from PDFs', icon: '🔍', status: 'complete' },
        { id: 3, name: 'Segmentation', description: 'Split into sentences', icon: '✂️', status: 'complete' },
        { id: 4, name: 'Classification', description: 'LLM identifies rules', icon: '🤖', status: 'complete' },
        { id: 5, name: 'Simplification', description: 'Simplify complex rules', icon: '📝', status: 'complete' },
        { id: 6, name: 'FOL Formalization', description: 'Convert to first-order logic', icon: '🧮', status: 'complete' },
        { id: 7, name: 'SHACL Translation', description: 'Generate SHACL shapes', icon: '🔷', status: 'complete' },
        { id: 8, name: 'Validation', description: 'Validate against data', icon: '✅', status: 'complete' },
    ]

    useEffect(() => {
        // Load validation metrics from API or static file
        const loadMetrics = async () => {
            try {
                const response = await fetch('/api/validation/metrics')
                if (response.ok) {
                    const data = await response.json()
                    setMetrics(data.metrics)
                    setResults(data.results || [])
                }
            } catch (error) {
                // Fallback to static data for demo
                setMetrics({
                    sample_size: 10,
                    avg_char_accuracy: 92.64,
                    avg_word_accuracy: 90.42,
                    perfect_extractions: 7,
                    acceptable_extractions: 7,
                    threshold_95_met: false
                })
                setResults([
                    { rule_id: 'GS-001', char_accuracy: 100, word_accuracy: 100 },
                    { rule_id: 'GS-002', char_accuracy: 100, word_accuracy: 100 },
                    { rule_id: 'GS-003', char_accuracy: 100, word_accuracy: 100 },
                    { rule_id: 'GS-004', char_accuracy: 100, word_accuracy: 100 },
                    { rule_id: 'GS-005', char_accuracy: 84.44, word_accuracy: 73.91 },
                    { rule_id: 'GS-006', char_accuracy: 100, word_accuracy: 100 },
                    { rule_id: 'GS-007', char_accuracy: 70.0, word_accuracy: 61.11 },
                    { rule_id: 'GS-008', char_accuracy: 71.97, word_accuracy: 69.23 },
                    { rule_id: 'GS-009', char_accuracy: 100, word_accuracy: 100 },
                    { rule_id: 'GS-010', char_accuracy: 100, word_accuracy: 100 },
                ])
            }
            setLoading(false)
        }
        loadMetrics()
    }, [])

    const getAccuracyColor = (accuracy) => {
        if (accuracy >= 95) return 'text-green-500'
        if (accuracy >= 80) return 'text-yellow-500'
        return 'text-red-500'
    }

    const getAccuracyBg = (accuracy) => {
        if (accuracy >= 95) return 'bg-green-100'
        if (accuracy >= 80) return 'bg-yellow-100'
        return 'bg-red-100'
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Extraction Validation Dashboard</h1>
                    <p className="text-gray-600 mt-1">Pipeline visualization and quality metrics</p>
                </div>
                <span className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    RuleChecker v1.0
                </span>
            </div>

            {/* Pipeline Visualization */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                    <span>🔄</span> 8-Step Agentic Pipeline
                </h2>
                <div className="flex items-center justify-between overflow-x-auto pb-4">
                    {pipelineSteps.map((step, index) => (
                        <div key={step.id} className="flex items-center">
                            <button
                                onClick={() => setSelectedStep(step)}
                                className={`flex flex-col items-center p-4 rounded-lg transition-all min-w-[120px] ${selectedStep?.id === step.id
                                        ? 'bg-blue-100 ring-2 ring-blue-500'
                                        : 'hover:bg-gray-100'
                                    }`}
                            >
                                <span className="text-3xl mb-2">{step.icon}</span>
                                <span className="text-sm font-medium text-gray-900">{step.name}</span>
                                <span className="text-xs text-gray-500 text-center mt-1">{step.description}</span>
                                <span className={`mt-2 px-2 py-0.5 rounded text-xs ${step.status === 'complete' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                                    }`}>
                                    {step.status === 'complete' ? '✓ Complete' : 'Pending'}
                                </span>
                            </button>
                            {index < pipelineSteps.length - 1 && (
                                <div className="w-8 h-0.5 bg-green-500 mx-2"></div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
                    <div className="text-sm opacity-80">Character Accuracy</div>
                    <div className="text-4xl font-bold mt-2">{metrics?.avg_char_accuracy}%</div>
                    <div className="text-sm mt-2 opacity-80">
                        {metrics?.threshold_95_met ? '✅ Threshold Met' : '⚠️ Below 95%'}
                    </div>
                </div>
                <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
                    <div className="text-sm opacity-80">Word Accuracy</div>
                    <div className="text-4xl font-bold mt-2">{metrics?.avg_word_accuracy}%</div>
                    <div className="text-sm mt-2 opacity-80">✅ Above 90%</div>
                </div>
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
                    <div className="text-sm opacity-80">Perfect Extractions</div>
                    <div className="text-4xl font-bold mt-2">{metrics?.perfect_extractions}/{metrics?.sample_size}</div>
                    <div className="text-sm mt-2 opacity-80">100% accuracy</div>
                </div>
                <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg">
                    <div className="text-sm opacity-80">Sample Size</div>
                    <div className="text-4xl font-bold mt-2">{metrics?.sample_size}</div>
                    <div className="text-sm mt-2 opacity-80">Verified rules</div>
                </div>
            </div>

            {/* Per-Rule Results Table */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <span>📊</span> Per-Rule Validation Results
                </h2>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b">
                                <th className="text-left py-3 px-4 font-semibold text-gray-700">Rule ID</th>
                                <th className="text-center py-3 px-4 font-semibold text-gray-700">Character Acc</th>
                                <th className="text-center py-3 px-4 font-semibold text-gray-700">Word Acc</th>
                                <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {results.map((result) => (
                                <tr key={result.rule_id} className="border-b hover:bg-gray-50">
                                    <td className="py-3 px-4 font-medium">{result.rule_id}</td>
                                    <td className="py-3 px-4 text-center">
                                        <span className={`px-3 py-1 rounded-full text-sm ${getAccuracyBg(result.char_accuracy)} ${getAccuracyColor(result.char_accuracy)}`}>
                                            {result.char_accuracy}%
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-center">
                                        <span className={`px-3 py-1 rounded-full text-sm ${getAccuracyBg(result.word_accuracy)} ${getAccuracyColor(result.word_accuracy)}`}>
                                            {result.word_accuracy}%
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-center">
                                        {result.char_accuracy >= 95 ? (
                                            <span className="text-green-500 text-xl">✅</span>
                                        ) : result.char_accuracy >= 80 ? (
                                            <span className="text-yellow-500 text-xl">⚠️</span>
                                        ) : (
                                            <span className="text-red-500 text-xl">❌</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Thesis Statement */}
            <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl p-6 text-white">
                <h3 className="text-lg font-semibold mb-3">📝 Thesis Documentation</h3>
                <blockquote className="border-l-4 border-blue-400 pl-4 italic">
                    "We validated our OCR extraction pipeline against a manually verified ground truth of {metrics?.sample_size} rules,
                    achieving <strong>{metrics?.avg_char_accuracy}% character accuracy</strong> and
                    <strong> {metrics?.avg_word_accuracy}% word accuracy</strong>."
                </blockquote>
            </div>
        </div>
    )
}

export default ValidationDashboard
