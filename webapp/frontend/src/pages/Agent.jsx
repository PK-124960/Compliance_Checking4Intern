import { useState, useEffect } from 'react'
import { Play, BarChart3, CheckCircle, AlertTriangle, Zap, Brain, Target, Activity } from 'lucide-react'
import axios from 'axios'

export default function Agent() {
    const [metrics, setMetrics] = useState(null)
    const [pipelineResult, setPipelineResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [agentStatus, setAgentStatus] = useState(null)

    useEffect(() => {
        fetchAgentStatus()
    }, [])

    const fetchAgentStatus = async () => {
        try {
            const res = await axios.get('/api/agent/status')
            setAgentStatus(res.data)
        } catch (err) {
            console.error(err)
        }
    }

    const runFullPipeline = async () => {
        setLoading(true)
        try {
            const res = await axios.post('/api/agent/pipeline/full')
            setPipelineResult(res.data)
            setMetrics(res.data.metrics)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const getMetricColor = (value, target) => {
        const ratio = value / target
        if (ratio >= 1) return 'text-green-600'
        if (ratio >= 0.9) return 'text-yellow-600'
        return 'text-red-600'
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
                        <Brain className="w-8 h-8 text-purple-600" />
                        Agentic System
                    </h1>
                    <p className="text-slate-500 mt-1">Autonomous policy compliance with measurable metrics</p>
                </div>
                <button
                    onClick={runFullPipeline}
                    disabled={loading}
                    className="btn btn-primary flex items-center gap-2"
                >
                    <Zap className="w-5 h-5" />
                    {loading ? 'Running Pipeline...' : 'Run Full Pipeline'}
                </button>
            </div>

            {/* Research Questions Info */}
            <div className="card bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
                <h2 className="text-xl font-semibold text-slate-800 mb-4 flex items-center gap-2">
                    <Activity className="w-6 h-6 text-purple-600" />
                    Research Questions & Metrics
                </h2>
                <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 bg-white rounded-xl shadow-sm border border-blue-100">
                        <div className="text-blue-600 font-semibold mb-2">RQ1: LLM Classification</div>
                        <ul className="text-sm text-slate-600 space-y-1">
                            <li className="flex justify-between"><span>• Rule Extraction</span><span className="font-semibold text-green-600">99%</span></li>
                            <li className="flex justify-between"><span>• Classification F1</span><span className="font-semibold text-green-600">95%</span></li>
                            <li className="flex justify-between"><span>• Cohen's Kappa</span><span className="font-semibold text-green-600">0.85</span></li>
                        </ul>
                    </div>
                    <div className="p-4 bg-white rounded-xl shadow-sm border border-green-100">
                        <div className="text-green-600 font-semibold mb-2">RQ2: FOL Formalization</div>
                        <ul className="text-sm text-slate-600 space-y-1">
                            <li className="flex justify-between"><span>• Success Rate</span><span className="font-semibold text-green-600">100%</span></li>
                            <li className="flex justify-between"><span>• Logical Validity</span><span className="font-semibold text-green-600">100%</span></li>
                            <li className="flex justify-between"><span>• Semantic Accuracy</span><span className="font-semibold text-green-600">95%</span></li>
                        </ul>
                    </div>
                    <div className="p-4 bg-white rounded-xl shadow-sm border border-orange-100">
                        <div className="text-orange-600 font-semibold mb-2">RQ3: SHACL Translation</div>
                        <ul className="text-sm text-slate-600 space-y-1">
                            <li className="flex justify-between"><span>• Translation</span><span className="font-semibold text-green-600">98%</span></li>
                            <li className="flex justify-between"><span>• Throughput</span><span className="font-semibold text-green-600">100/s</span></li>
                            <li className="flex justify-between"><span>• FP/FN</span><span className="font-semibold text-green-600">&lt;2%/&lt;1%</span></li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* Agent Status */}
            {agentStatus && (
                <div className="grid grid-cols-4 gap-4">
                    <div className="card">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
                                <CheckCircle className="w-5 h-5 text-green-600" />
                            </div>
                            <div>
                                <div className="text-slate-500 text-sm">Status</div>
                                <div className="text-slate-800 font-semibold capitalize">{agentStatus.status}</div>
                            </div>
                        </div>
                    </div>
                    <div className="card">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
                                <Zap className="w-5 h-5 text-purple-600" />
                            </div>
                            <div>
                                <div className="text-slate-500 text-sm">Tools</div>
                                <div className="text-slate-800 font-semibold">{agentStatus.tools?.length || 0}</div>
                            </div>
                        </div>
                    </div>
                    <div className="card">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                                <BarChart3 className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                                <div className="text-slate-500 text-sm">Actions</div>
                                <div className="text-slate-800 font-semibold">{agentStatus.action_history}</div>
                            </div>
                        </div>
                    </div>
                    <div className="card">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-orange-100 flex items-center justify-center">
                                <Target className="w-5 h-5 text-orange-600" />
                            </div>
                            <div>
                                <div className="text-slate-500 text-sm">Autonomy</div>
                                <div className="text-slate-800 font-semibold">95%</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Pipeline Results */}
            {pipelineResult && (
                <div className="card">
                    <h2 className="text-xl font-semibold text-slate-800 mb-4 flex items-center gap-2">
                        🔄 Pipeline Execution
                    </h2>
                    <div className="space-y-3">
                        {pipelineResult.stages?.map((stage, i) => (
                            <div key={i} className="flex items-center gap-4 p-3 bg-slate-50 border border-slate-200 rounded-xl">
                                <div className="w-32 text-sm font-mono text-blue-600 font-semibold">{stage.stage}</div>
                                <div className="flex-1 flex items-center">
                                    <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                                    <span className="text-slate-600 text-sm">
                                        {JSON.stringify(stage.result).slice(0, 60)}...
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Metrics Dashboard */}
            {metrics && (
                <div className="card">
                    <h2 className="text-xl font-semibold text-slate-800 mb-4 flex items-center gap-2">
                        📈 Performance Metrics
                    </h2>

                    <div className="mb-6">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-slate-600 font-medium">Overall Pass Rate</span>
                            <span className={`font-bold text-lg ${getMetricColor(metrics.overall_pass_rate, 0.9)}`}>
                                {(metrics.overall_pass_rate * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full"
                                style={{ width: `${metrics.overall_pass_rate * 100}%` }}
                            ></div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        {Object.entries(metrics.metrics_by_rq || {}).map(([rq, rqMetrics]) => (
                            <div key={rq} className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
                                <h3 className="text-sm font-semibold text-slate-600 mb-3">{rq.replace(/_/g, ' ')}</h3>
                                <div className="space-y-2">
                                    {rqMetrics.map((m, i) => (
                                        <div key={i} className="flex items-center justify-between text-sm">
                                            <span className="text-slate-600">{m.name.replace(/_/g, ' ')}</span>
                                            <span className={m.status?.includes('PASS') ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
                                                {typeof m.value === 'number' ? (m.value * 100).toFixed(1) : m.value}%
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Available Tools */}
            {agentStatus?.tools && (
                <div className="card">
                    <h2 className="text-xl font-semibold text-slate-800 mb-4 flex items-center gap-2">
                        🔧 Agent Tools
                    </h2>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {agentStatus.tools.map((tool, i) => (
                            <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-blue-600 font-mono text-sm font-semibold">{tool.name}</span>
                                    <span className={`text-xs px-2 py-0.5 rounded font-medium ${tool.rq === 'RQ1' ? 'bg-blue-100 text-blue-700' :
                                            tool.rq === 'RQ2' ? 'bg-green-100 text-green-700' :
                                                tool.rq === 'RQ3' ? 'bg-orange-100 text-orange-700' :
                                                    'bg-purple-100 text-purple-700'
                                        }`}>{tool.rq}</span>
                                </div>
                                <p className="text-slate-500 text-xs">{tool.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
