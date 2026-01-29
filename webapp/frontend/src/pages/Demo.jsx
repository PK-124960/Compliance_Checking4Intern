import { useState, useEffect } from 'react'
import { Users, AlertTriangle, CheckCircle, Play, FileText, Shield } from 'lucide-react'
import axios from 'axios'

export default function Demo() {
    const [students, setStudents] = useState([])
    const [report, setReport] = useState(null)
    const [loading, setLoading] = useState(false)
    const [selectedStudent, setSelectedStudent] = useState(null)

    useEffect(() => {
        fetchStudents()
    }, [])

    const fetchStudents = async () => {
        try {
            const res = await axios.get('/api/demo/students')
            setStudents(res.data)
        } catch (err) {
            console.error(err)
        }
    }

    const runComplianceCheck = async () => {
        setLoading(true)
        try {
            const res = await axios.get('/api/demo/check-all')
            setReport(res.data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const checkStudent = async (studentId) => {
        try {
            const res = await axios.get(`/api/demo/check/${studentId}`)
            setSelectedStudent(res.data)
        } catch (err) {
            console.error(err)
        }
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">🎓 Real-World Demo</h1>
                    <p className="text-slate-400 mt-1">Automated Student Policy Compliance Verification</p>
                </div>
                <button
                    onClick={runComplianceCheck}
                    disabled={loading}
                    className="btn btn-primary flex items-center gap-2"
                >
                    <Play className="w-5 h-5" />
                    {loading ? 'Checking...' : 'Run Compliance Check'}
                </button>
            </div>

            {/* Use Case Description */}
            <div className="card bg-gradient-to-r from-blue-900/50 to-purple-900/50 border-blue-500/30">
                <h2 className="text-xl font-semibold text-white mb-3">📋 Use Case: University Registrar Office</h2>
                <p className="text-slate-300">
                    This demonstrates how PolicyChecker can automatically verify student compliance against
                    formalized policy rules. The system uses an <strong className="text-blue-400">intelligent rule engine</strong> powered
                    by the extracted FOL rules to check each student's status.
                </p>
                <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                        <Shield className="w-6 h-6 text-green-400 mx-auto mb-2" />
                        <div className="text-sm text-slate-400">Automated Checking</div>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                        <FileText className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                        <div className="text-sm text-slate-400">96 Policy Rules</div>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                        <AlertTriangle className="w-6 h-6 text-orange-400 mx-auto mb-2" />
                        <div className="text-sm text-slate-400">Real-time Alerts</div>
                    </div>
                </div>
            </div>

            {/* Students Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {students.map((student) => {
                    const result = report?.student_results?.find(r => r.student_id === student.id)
                    return (
                        <div
                            key={student.id}
                            onClick={() => checkStudent(student.id)}
                            className={`card card-hover cursor-pointer ${result?.is_compliant === false ? 'border-red-500/50' :
                                    result?.is_compliant === true ? 'border-green-500/50' : ''
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-white font-semibold">{student.name}</span>
                                        <span className="text-xs text-slate-500">{student.id}</span>
                                    </div>
                                    <p className="text-slate-400 text-sm mt-1">{student.program}</p>
                                    <div className="flex items-center gap-2 mt-2">
                                        <span className={`badge ${student.status === 'enrolled' ? 'bg-green-500/20 text-green-400' :
                                                student.status === 'graduated' ? 'bg-blue-500/20 text-blue-400' :
                                                    'bg-red-500/20 text-red-400'
                                            }`}>
                                            {student.status}
                                        </span>
                                        {!student.fees_paid && (
                                            <span className="badge bg-orange-500/20 text-orange-400">Unpaid</span>
                                        )}
                                    </div>
                                </div>
                                {result && (
                                    <div className={`flex items-center gap-1 ${result.is_compliant ? 'text-green-400' : 'text-red-400'
                                        }`}>
                                        {result.is_compliant ? (
                                            <CheckCircle className="w-6 h-6" />
                                        ) : (
                                            <AlertTriangle className="w-6 h-6" />
                                        )}
                                        <span className="text-sm font-semibold">{result.violations}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Compliance Report */}
            {report && (
                <div className="card">
                    <h2 className="text-xl font-semibold text-white mb-4">📊 Compliance Report</h2>
                    <div className="grid grid-cols-4 gap-4 mb-6">
                        <div className="text-center p-4 bg-slate-900 rounded-xl">
                            <div className="text-3xl font-bold text-white">{report.total_students}</div>
                            <div className="text-slate-400 text-sm">Total Students</div>
                        </div>
                        <div className="text-center p-4 bg-slate-900 rounded-xl">
                            <div className="text-3xl font-bold text-green-400">{report.compliant_students}</div>
                            <div className="text-slate-400 text-sm">Compliant</div>
                        </div>
                        <div className="text-center p-4 bg-slate-900 rounded-xl">
                            <div className="text-3xl font-bold text-red-400">{report.non_compliant_students}</div>
                            <div className="text-slate-400 text-sm">Non-Compliant</div>
                        </div>
                        <div className="text-center p-4 bg-slate-900 rounded-xl">
                            <div className="text-3xl font-bold text-orange-400">{report.total_violations}</div>
                            <div className="text-slate-400 text-sm">Violations</div>
                        </div>
                    </div>

                    <div className={`p-4 rounded-xl ${report.total_violations > 0 ? 'bg-red-500/10 border border-red-500/30' : 'bg-green-500/10 border border-green-500/30'
                        }`}>
                        <div className="flex items-center gap-2">
                            {report.total_violations > 0 ? (
                                <AlertTriangle className="w-5 h-5 text-red-400" />
                            ) : (
                                <CheckCircle className="w-5 h-5 text-green-400" />
                            )}
                            <span className={report.total_violations > 0 ? 'text-red-400' : 'text-green-400'}>
                                {report.summary.status}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Student Detail Modal */}
            {selectedStudent && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedStudent(null)}>
                    <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
                        <div className="p-6 border-b border-slate-700">
                            <h2 className="text-xl font-semibold text-white">
                                Compliance Check: {selectedStudent.student_name}
                            </h2>
                            <p className="text-slate-400 text-sm">ID: {selectedStudent.student_id}</p>
                        </div>

                        <div className="p-6 space-y-4">
                            <div className="flex items-center justify-between p-4 bg-slate-800 rounded-xl">
                                <span className="text-slate-400">Compliance Rate</span>
                                <span className={`text-2xl font-bold ${selectedStudent.compliance_rate === 100 ? 'text-green-400' : 'text-orange-400'
                                    }`}>
                                    {selectedStudent.compliance_rate}%
                                </span>
                            </div>

                            {selectedStudent.violation_details.length > 0 && (
                                <div>
                                    <h3 className="text-red-400 font-semibold mb-2">⚠️ Violations</h3>
                                    <div className="space-y-2">
                                        {selectedStudent.violation_details.map((v, i) => (
                                            <div key={i} className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs text-red-400 font-mono">{v.rule_id}</span>
                                                    <span className="badge badge-obligation">{v.type}</span>
                                                </div>
                                                <p className="text-white mt-1">{v.violation}</p>
                                                <p className="text-slate-400 text-sm">{v.description}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div>
                                <h3 className="text-green-400 font-semibold mb-2">✓ Passed Rules</h3>
                                <div className="space-y-1">
                                    {selectedStudent.passed_rules.map((r, i) => (
                                        <div key={i} className="flex items-center gap-2 text-sm text-slate-400">
                                            <CheckCircle className="w-4 h-4 text-green-400" />
                                            <span>{r.description}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
