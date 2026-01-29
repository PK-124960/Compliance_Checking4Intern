import { useState, useEffect } from 'react'
import { FileText, Code, Shield, CheckCircle, TrendingUp, Users, BarChart3 } from 'lucide-react'
import axios from 'axios'

export default function Dashboard() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchStats()
    }, [])

    const fetchStats = async () => {
        try {
            const res = await axios.get('/api/stats')
            setStats(res.data)
        } catch (err) {
            console.error('Failed to fetch stats:', err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    const statCards = [
        { label: 'Total Rules', value: stats?.total_rules || 0, icon: FileText, color: 'blue', bg: 'bg-blue-50' },
        { label: 'Formalized', value: stats?.formalized || 0, icon: Code, color: 'purple', bg: 'bg-purple-50' },
        { label: 'SHACL Triples', value: stats?.shacl_triples || 0, icon: Shield, color: 'green', bg: 'bg-green-50' },
        { label: 'Annotated', value: stats?.annotated || 0, icon: CheckCircle, color: 'emerald', bg: 'bg-emerald-50' },
    ]

    const ruleTypes = [
        { type: 'Obligations', count: stats?.obligations || 0, color: 'red', percentage: ((stats?.obligations || 0) / (stats?.formalized || 1)) * 100 },
        { type: 'Permissions', count: stats?.permissions || 0, color: 'green', percentage: ((stats?.permissions || 0) / (stats?.formalized || 1)) * 100 },
        { type: 'Prohibitions', count: stats?.prohibitions || 0, color: 'orange', percentage: ((stats?.prohibitions || 0) / (stats?.formalized || 1)) * 100 },
    ]

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-slate-800">Dashboard</h1>
                <p className="text-slate-500 mt-2">Overview of your policy formalization pipeline</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statCards.map((stat, i) => (
                    <div key={i} className="card card-hover">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-slate-500 text-sm font-medium">{stat.label}</p>
                                <p className="text-3xl font-bold text-slate-800 mt-1">{stat.value}</p>
                            </div>
                            <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center`}>
                                <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Rule Types */}
            <div className="card">
                <h2 className="text-xl font-semibold text-slate-800 mb-6">Rule Distribution</h2>
                <div className="grid grid-cols-3 gap-6">
                    {ruleTypes.map((item, i) => (
                        <div key={i} className="text-center">
                            <div className={`text-4xl font-bold text-${item.color}-600`}>{item.count}</div>
                            <div className="text-slate-500 mt-1 font-medium">{item.type}</div>
                            <div className="mt-4 h-2 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className={`h-full bg-${item.color}-500 rounded-full`}
                                    style={{ width: `${item.percentage}%` }}
                                ></div>
                            </div>
                            <div className="text-sm text-slate-400 mt-1">{item.percentage.toFixed(1)}%</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Progress */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                    <h2 className="text-xl font-semibold text-slate-800 mb-4">Annotation Progress</h2>
                    <div className="flex items-center gap-4">
                        <div className="flex-1">
                            <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full"
                                    style={{ width: `${((stats?.annotated || 0) / (stats?.total_rules || 1)) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                        <span className="text-slate-800 font-bold text-lg">
                            {Math.round(((stats?.annotated || 0) / (stats?.total_rules || 1)) * 100)}%
                        </span>
                    </div>
                    <p className="text-slate-500 text-sm mt-3">
                        {stats?.annotated} of {stats?.total_rules} rules annotated
                    </p>
                </div>

                <div className="card">
                    <h2 className="text-xl font-semibold text-slate-800 mb-4">Pipeline Status</h2>
                    <div className="space-y-3">
                        {[
                            { step: 'PDF Extraction', status: 'complete' },
                            { step: 'LLM Classification', status: 'complete' },
                            { step: 'FOL Formalization', status: 'complete' },
                            { step: 'SHACL Translation', status: 'complete' },
                        ].map((item, i) => (
                            <div key={i} className="flex items-center gap-3 p-2 bg-green-50 rounded-lg">
                                <CheckCircle className="w-5 h-5 text-green-600" />
                                <span className="text-slate-700 font-medium">{item.step}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
