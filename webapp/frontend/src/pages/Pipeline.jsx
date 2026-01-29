import { useState, useEffect } from 'react'
import {
    FileText, Brain, Code, Shield, Play, ChevronRight,
    CheckCircle, Clock, Database, Zap, BarChart3, Download
} from 'lucide-react'
import axios from 'axios'

const PIPELINE_STEPS = [
    {
        id: 1,
        name: 'Document Processing',
        icon: FileText,
        rq: null,
        description: 'Extract text from policy PDFs',
        input: '5 AIT Policy PDFs',
        output: '492 candidate sentences',
        metrics: { documents: 5, sentences: 492, pages: 47 },
        color: 'blue'
    },
    {
        id: 2,
        name: 'LLM Classification',
        icon: Brain,
        rq: 'RQ1',
        description: 'Identify policy rules using Mistral 7B',
        input: '492 sentences',
        output: '97 policy rules identified',
        metrics: { rules: 97, accuracy: 99, f1: 95, kappa: 0.85 },
        color: 'purple'
    },
    {
        id: 3,
        name: 'FOL Formalization',
        icon: Code,
        rq: 'RQ2',
        description: 'Convert rules to First-Order Logic',
        input: '97 rules',
        output: '96 FOL formulas',
        metrics: { success: 100, obligations: 65, permissions: 17, prohibitions: 14 },
        color: 'green'
    },
    {
        id: 4,
        name: 'SHACL Translation',
        icon: Shield,
        rq: 'RQ3',
        description: 'Generate validation constraints',
        input: '96 FOL formulas',
        output: '1,309 SHACL triples',
        metrics: { triples: 1309, shapes: 96, valid: true },
        color: 'orange'
    }
]

export default function Pipeline() {
    const [activeStep, setActiveStep] = useState(null)
    const [executing, setExecuting] = useState(false)
    const [executionResults, setExecutionResults] = useState([])
    const [currentStep, setCurrentStep] = useState(0)

    const runPipeline = async () => {
        setExecuting(true)
        setExecutionResults([])
        setCurrentStep(0)

        for (let i = 0; i < PIPELINE_STEPS.length; i++) {
            setCurrentStep(i + 1)

            // Simulate step execution
            await new Promise(resolve => setTimeout(resolve, 1500))

            setExecutionResults(prev => [...prev, {
                step: i + 1,
                name: PIPELINE_STEPS[i].name,
                status: 'success',
                time: (Math.random() * 5 + 1).toFixed(2)
            }])
        }

        setExecuting(false)
    }

    const getColorClasses = (color, type = 'bg') => {
        const colors = {
            blue: { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200' },
            purple: { bg: 'bg-purple-100', text: 'text-purple-600', border: 'border-purple-200' },
            green: { bg: 'bg-green-100', text: 'text-green-600', border: 'border-green-200' },
            orange: { bg: 'bg-orange-100', text: 'text-orange-600', border: 'border-orange-200' }
        }
        return colors[color][type]
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
                        <Zap className="w-8 h-8 text-blue-600" />
                        Pipeline Execution
                    </h1>
                    <p className="text-slate-500 mt-1">Step-by-step policy formalization process</p>
                </div>
                <button
                    onClick={runPipeline}
                    disabled={executing}
                    className="btn btn-primary flex items-center gap-2"
                >
                    <Play className="w-5 h-5" />
                    {executing ? `Running Step ${currentStep}/4...` : 'Run Full Pipeline'}
                </button>
            </div>

            {/* Pipeline Flow */}
            <div className="card">
                <h2 className="text-lg font-semibold text-slate-800 mb-6">Pipeline Flow</h2>

                <div className="relative">
                    {/* Connection Line */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-slate-200 -translate-x-1/2 z-0"></div>

                    {/* Steps */}
                    <div className="relative z-10 space-y-8">
                        {PIPELINE_STEPS.map((step, index) => {
                            const isComplete = executionResults.some(r => r.step === step.id)
                            const isCurrent = currentStep === step.id && executing
                            const result = executionResults.find(r => r.step === step.id)

                            return (
                                <div key={step.id} className="relative">
                                    {/* Step Card */}
                                    <div
                                        className={`relative ml-8 mr-8 card card-hover cursor-pointer transition-all ${isCurrent ? 'ring-2 ring-blue-500 ring-offset-2' : ''
                                            } ${activeStep === step.id ? 'bg-slate-50' : ''}`}
                                        onClick={() => setActiveStep(activeStep === step.id ? null : step.id)}
                                    >
                                        {/* Step Number Circle */}
                                        <div className={`absolute -left-12 top-6 w-8 h-8 rounded-full flex items-center justify-center font-bold ${isComplete ? 'bg-green-500 text-white' :
                                                isCurrent ? 'bg-blue-500 text-white animate-pulse' :
                                                    'bg-slate-200 text-slate-600'
                                            }`}>
                                            {isComplete ? <CheckCircle className="w-5 h-5" /> : step.id}
                                        </div>

                                        {/* Content */}
                                        <div className="flex items-start gap-4">
                                            <div className={`w-12 h-12 rounded-xl ${getColorClasses(step.color, 'bg')} flex items-center justify-center`}>
                                                <step.icon className={`w-6 h-6 ${getColorClasses(step.color, 'text')}`} />
                                            </div>

                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <h3 className="font-semibold text-slate-800">{step.name}</h3>
                                                    {step.rq && (
                                                        <span className={`text-xs font-medium px-2 py-0.5 rounded ${getColorClasses(step.color, 'bg')} ${getColorClasses(step.color, 'text')}`}>
                                                            {step.rq}
                                                        </span>
                                                    )}
                                                    {result && (
                                                        <span className="text-xs text-green-600 flex items-center gap-1">
                                                            <Clock className="w-3 h-3" /> {result.time}s
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-slate-500 text-sm mt-1">{step.description}</p>

                                                <div className="flex items-center gap-4 mt-3 text-sm">
                                                    <div className="flex items-center gap-1 text-slate-500">
                                                        <span className="font-medium">Input:</span> {step.input}
                                                    </div>
                                                    <ChevronRight className="w-4 h-4 text-slate-400" />
                                                    <div className="flex items-center gap-1 text-slate-700 font-medium">
                                                        <span>Output:</span> {step.output}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Expanded Metrics */}
                                        {activeStep === step.id && (
                                            <div className="mt-4 pt-4 border-t border-slate-100">
                                                <h4 className="text-sm font-semibold text-slate-600 mb-3">Metrics</h4>
                                                <div className="grid grid-cols-4 gap-3">
                                                    {Object.entries(step.metrics).map(([key, value]) => (
                                                        <div key={key} className="text-center p-2 bg-slate-50 rounded-lg">
                                                            <div className="text-lg font-bold text-slate-800">
                                                                {typeof value === 'boolean' ? (value ? '✅' : '❌') : value}
                                                                {key === 'accuracy' || key === 'f1' || key === 'success' ? '%' : ''}
                                                            </div>
                                                            <div className="text-xs text-slate-500 capitalize">{key.replace('_', ' ')}</div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            </div>

            {/* Execution Summary */}
            {executionResults.length === 4 && (
                <div className="card bg-green-50 border-green-200">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                            <CheckCircle className="w-6 h-6 text-green-600" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-green-800">Pipeline Complete!</h3>
                            <p className="text-green-700 text-sm">
                                Total execution time: {executionResults.reduce((acc, r) => acc + parseFloat(r.time), 0).toFixed(2)}s
                            </p>
                        </div>
                        <div className="ml-auto flex gap-2">
                            <button className="btn btn-secondary flex items-center gap-2">
                                <Download className="w-4 h-4" /> Export Results
                            </button>
                            <button className="btn btn-success flex items-center gap-2">
                                <BarChart3 className="w-4 h-4" /> View Metrics
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Research Questions Summary */}
            <div className="grid grid-cols-3 gap-4">
                <div className="card">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center">
                            <Brain className="w-4 h-4 text-purple-600" />
                        </div>
                        <span className="font-semibold text-slate-800">RQ1</span>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">Can LLMs effectively identify policy rules?</p>
                    <div className="text-2xl font-bold text-green-600">99% Accuracy</div>
                    <div className="text-xs text-slate-500">Mistral 7B, κ = 0.85</div>
                </div>

                <div className="card">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
                            <Code className="w-4 h-4 text-green-600" />
                        </div>
                        <span className="font-semibold text-slate-800">RQ2</span>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">Is FOL sufficient for policy formalization?</p>
                    <div className="text-2xl font-bold text-green-600">100% Success</div>
                    <div className="text-xs text-slate-500">65O + 17P + 14F = 96 rules</div>
                </div>

                <div className="card">
                    <div className="flex items-center gap-2 mb-3">
                        <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center">
                            <Shield className="w-4 h-4 text-orange-600" />
                        </div>
                        <span className="font-semibold text-slate-800">RQ3</span>
                    </div>
                    <p className="text-sm text-slate-600 mb-3">Can FOL be translated to SHACL?</p>
                    <div className="text-2xl font-bold text-green-600">1,309 Triples</div>
                    <div className="text-xs text-slate-500">96 shapes validated</div>
                </div>
            </div>
        </div>
    )
}
