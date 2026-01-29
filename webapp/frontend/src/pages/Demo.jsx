import { useState, useEffect } from 'react'
import { Users, AlertTriangle, CheckCircle, Play, FileText, Shield, Building2 } from 'lucide-react'
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
                    <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
                        <span className="text-3xl">🎓</span> Real-World Demo
                    </h1>
                    <p className="text-slate-500 mt-1">Automated Student Policy Compliance Verification</p>
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
            <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-semibold text-slate-800 mb-2">Use Case: University Registrar Office</h2>
                        <p className="text-slate-600">
                            This demonstrates how PolicyChecker can automatically verify student compliance against
                            formalized policy rules. The system uses an <strong className="text-blue-600">intelligent rule engine</strong> powered
                            by the extracted FOL rules to check each student's status.
                        </p>
                    </div>
                </div>
                <div className="mt-6 grid grid-cols-3 gap-4 text-center">
                    <div className="p-4 bg-white rounded-xl shadow-sm">
                        <Shield className="w-6 h-6 text-green-600 mx-auto mb-2" />
                        <div className="text-sm text-slate-600 font-medium">Automated Checking</div>
                    </div>
                    <div className="p-4 bg-white rounded-xl shadow-sm">
                        <FileText className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                        <div className="text-sm text-slate-600 font-medium">96 Policy Rules</div>
                    </div>
                    <div className="p-4 bg-white rounded-xl shadow-sm">
                        <AlertTriangle className="w-6 h-6 text-orange-600 mx-auto mb-2" />
                        <div className="text-sm text-slate-600 font-medium">Real-time Alerts</div>
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
                            className={`card card-hover cursor-pointer ${result?.is_compliant === false ? 'border-red-300 bg-red-50/50' :
                                    result?.is_compliant === true ? 'border-green-300 bg-green-50/50' : ''
                                }`}
                        >
                            <div className="flex items-start justify-between">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-slate-800 font-semibold text-lg">{student.name}</span>
                                        <span className="text-xs text-slate-400 font-mono">{student.id}</span>
                                    </div>
                                    <p className="text-slate-500 text-sm mt-1">{student.program}</p>
                                    <div className="flex items-center gap-2 mt-3">
                                        <span className={`px-3 py-1 rounded-lg text-xs font-medium ${student.status === 'enrolled' ? 'bg-green-100 text-green-700' :
                                                student.status === 'graduated' ? 'bg-blue-100 text-blue-700' :
                                                    'bg-red-100 text-red-700'
                                            }`}>
                                            {student.status}
                                        </span>
                                        {!student.fees_paid && (
                                            <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-lg text-xs font-medium">Unpaid</span>
                                        )}
                                    </div>
                                </div>
                                {result && (
                                    <div className={`flex items-center gap-1 px-3 py-1 rounded-lg ${result.is_compliant ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                        }`}>
                                        {result.is_compliant ? (
                                            <CheckCircle className="w-5 h-5" />
                                        ) : (
                                            <AlertTriangle className="w-5 h-5" />
                                        )}
                                        <span className="text-sm font-bold">{result.violations}</span>
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
                    <h2 className="text-xl font-semibold text-slate-800 mb-4 flex items-center gap-2">
                        <span>📊</span> Compliance Report
                    </h2>
                    <div className="grid grid-cols-4 gap-4 mb-6">
                        <div className="text-center p-4 bg-slate-50 rounded-xl border border-slate-200">
                            <div className="text-3xl font-bold text-slate-800">{report.total_students}</div>
                            <div className="text-slate-500 text-sm font-medium">Total Students</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-xl border border-green-200">
                            <div className="text-3xl font-bold text-green-600">{report.compliant_students}</div>
                            <div className="text-slate-500 text-sm font-medium">Compliant</div>
                        </div>
                        <div className="text-center p-4 bg-red-50 rounded-xl border border-red-200">
                            <div className="text-3xl font-bold text-red-600">{report.non_compliant_students}</div>
                            <div className="text-slate-500 text-sm font-medium">Non-Compliant</div>
                        </div>
                        <div className="text-center p-4 bg-orange-50 rounded-xl border border-orange-200">
                            <div className="text-3xl font-bold text-orange-600">{report.total_violations}</div>
                            <div className="text-slate-500 text-sm font-medium">Violations</div>
                        </div>
                    </div>

                    <div className={`p-4 rounded-xl flex items-center gap-3 ${report.total_violations > 0 ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'
                        }`}>
                        {report.total_violations > 0 ? (
                            <AlertTriangle className="w-6 h-6 text-red-600" />
                        ) : (
                            <CheckCircle className="w-6 h-6 text-green-600" />
                        )}
                        <span className={`font-semibold ${report.total_violations > 0 ? 'text-red-700' : 'text-green-700'}`}>
                            {report.summary.status}
                        </span>
                    </div>
                </div>
            )}

            {/* Student Detail Modal */}
            {selectedStudent && (
                <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setSelectedStudent(null)}>
                    <div className="bg-white border border-slate-200 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
                        <div className="p-6 border-b border-slate-100">
                            <h2 className="text-xl font-semibold text-slate-800">
                                Compliance Check: {selectedStudent.student_name}
                            </h2>
                            <p className="text-slate-500 text-sm">ID: {selectedStudent.student_id}</p>
                        </div>

                        <div className="p-6 space-y-6">
                            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                                <span className="text-slate-600 font-medium">Compliance Rate</span>
                                <span className={`text-3xl font-bold ${selectedStudent.compliance_rate === 100 ? 'text-green-600' : 'text-orange-600'
                                    }`}>
                                    {selectedStudent.compliance_rate}%
                                </span>
                            </div>

                            {selectedStudent.violation_details.length > 0 && (
                                <div>
                                    <h3 className="text-red-600 font-semibold mb-3 flex items-center gap-2">
                                        <AlertTriangle className="w-5 h-5" /> Violations
                                    </h3>
                                    <div className="space-y-2">
                                        {selectedStudent.violation_details.map((v, i) => (
                                            <div key={i} className="p-4 bg-red-50 border border-red-200 rounded-xl">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="text-xs text-red-600 font-mono bg-red-100 px-2 py-0.5 rounded">{v.rule_id}</span>
                                                    <span className="badge badge-obligation">{v.type}</span>
                                                </div>
                                                <p className="text-red-800 font-medium">{v.msg}</p>
                                                <p className="text-slate-600 text-sm">{v.description}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div>
                                <h3 className="text-green-600 font-semibold mb-3 flex items-center gap-2">
                                    <CheckCircle className="w-5 h-5" /> Passed Rules
                                </h3>
                                <div className="space-y-1">
                                    {selectedStudent.passed_rules.map((r, i) => (
                                        <div key={i} className="flex items-center gap-2 text-sm p-2 bg-green-50 rounded-lg">
                                            <CheckCircle className="w-4 h-4 text-green-600" />
                                            <span className="text-slate-700">{r.description}</span>
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
