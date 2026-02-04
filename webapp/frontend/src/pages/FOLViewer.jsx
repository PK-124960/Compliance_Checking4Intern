import { useState, useEffect } from 'react'
import { Code, Search, Eye, X, Sparkles, BookOpen } from 'lucide-react'
import axios from 'axios'

export default function FOLViewer() {
    const [folData, setFolData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [selectedFormula, setSelectedFormula] = useState(null)
    const [searchTerm, setSearchTerm] = useState('')
    const [filterType, setFilterType] = useState('All')

    useEffect(() => {
        fetchFOLData()
    }, [])

    const fetchFOLData = async () => {
        try {
            const res = await axios.get('/api/fol-results')
            console.log('FOL API response:', res.data)
            setFolData(res.data)
        } catch (err) {
            console.error('Failed to fetch FOL formulas:', err)
            // Fallback: load from local file
            loadLocalData()
        } finally {
            setLoading(false)
        }
    }

    const loadLocalData = () => {
        axios.get('/research/fol_formalization_v2_results.json')
            .then(res => {
                console.log('Loaded local FOL data:', res.data)
                setFolData(res.data)
            })
            .catch(err => console.error('Failed to load local FOL data:', err))
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="processing-spinner w-8 h-8 border-blue-600"></div>
            </div>
        )
    }

    const formulas = folData?.formalized_rules || []
    const metadata = folData?.metadata || {}

    // Filter formulas
    const filteredFormulas = formulas.filter(f => {
        const deonticType = f.fol_formalization?.deontic_type || ''
        const ruleId = f.id || ''
        const originalText = f.original_text || ''
        const formula = f.fol_formalization?.fol_expansion || ''

        const matchesSearch = ruleId.toLowerCase().includes(searchTerm.toLowerCase()) ||
            originalText.toLowerCase().includes(searchTerm.toLowerCase()) ||
            formula.toLowerCase().includes(searchTerm.toLowerCase())

        const matchesFilter = filterType === 'All' ||
            deonticType.toLowerCase() === filterType.toLowerCase()

        return matchesSearch && matchesFilter
    })

    // Count by type
    const typeCounts = {
        All: formulas.length,
        Obligation: formulas.filter(f => f.fol_formalization?.deontic_type === 'obligation').length,
        Permission: formulas.filter(f => f.fol_formalization?.deontic_type === 'permission').length,
        Prohibition: formulas.filter(f => f.fol_formalization?.deontic_type === 'prohibition').length
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-4xl font-bold text-gray-800 flex items-center gap-3">
                    <Code className="w-10 h-10 text-green-600" />
                    First-Order Logic Formulas
                </h1>
                <p className="text-gray-600 mt-2 text-lg">
                    {formulas.length} policy rules formalized in FOL (Phase 3 result)
                </p>
            </div>

            {/* Metadata */}
            {metadata.model && (
                <div className="card bg-gradient-to-r from-purple-50 to-blue-50 border-l-4 border-purple-500">
                    <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-purple-600" />
                        Formalization Metadata
                    </h3>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                            <strong>Model:</strong> {metadata.model}
                        </div>
                        <div>
                            <strong>Version:</strong> {metadata.version}
                        </div>
                        <div>
                            <strong>Total Rules:</strong> {metadata.total_rules}
                        </div>
                    </div>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <div className="card bg-green-50 text-center">
                    <div className="text-4xl font-bold text-green-700">{formulas.length}</div>
                    <div className="text-sm text-green-600 mt-1 font-medium">Total Formulas</div>
                </div>
                <div className="card bg-red-50 text-center">
                    <div className="text-4xl font-bold text-red-700">{typeCounts.Obligation}</div>
                    <div className="text-sm text-red-600 mt-1 font-medium">Obligations</div>
                </div>
                <div className="card bg-blue-50 text-center">
                    <div className="text-4xl font-bold text-blue-700">{typeCounts.Permission}</div>
                    <div className="text-sm text-blue-600 mt-1 font-medium">Permissions</div>
                </div>
                <div className="card bg-orange-50 text-center">
                    <div className="text-4xl font-bold text-orange-700">{typeCounts.Prohibition}</div>
                    <div className="text-sm text-orange-600 mt-1 font-medium">Prohibitions</div>
                </div>
            </div>

            {/* Key Finding */}
            <div className="card bg-gradient-to-r from-green-50 to-green-100 border-l-4 border-green-500">
                <h3 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
                    <Code className="w-5 h-5" />
                    Research Finding (RQ2)
                </h3>
                <p className="text-green-700">
                    <strong>FOL is sufficient</strong> for institutional policy formalization. No higher-order logic required.
                </p>
            </div>

            {/* Filters */}
            <div className="card">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            <Search className="w-4 h-4 inline mr-1" />
                            Search Formulas
                        </label>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Search by rule ID, text, or formula..."
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Type</label>
                        <div className="flex gap-2">
                            {['All', 'Obligation', 'Permission', 'Prohibition'].map(type => (
                                <button
                                    key={type}
                                    onClick={() => setFilterType(type)}
                                    className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${filterType === type
                                            ? 'bg-green-600 text-white'
                                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                        }`}
                                >
                                    {type} ({typeCounts[type]})
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Formula Grid */}
            <div className="grid grid-cols-2 gap-4">
                {filteredFormulas.map((formula, idx) => {
                    const deonticType = formula.fol_formalization?.deontic_type || 'unknown'
                    const folFormula = formula.fol_formalization?.fol_expansion || 'N/A'
                    const deonticFormula = formula.fol_formalization?.deontic_formula || 'N/A'
                    const ruleId = formula.id || `F${idx + 1}`

                    return (
                        <div
                            key={idx}
                            className="card hover:shadow-xl transition-all cursor-pointer"
                            onClick={() => setSelectedFormula(formula)}
                        >
                            <div className="flex items-start gap-3 mb-3">
                                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center font-bold text-green-700 text-sm flex-shrink-0">
                                    {idx + 1}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="text-sm text-gray-600 mb-1 font-mono">{ruleId}</div>
                                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${deonticType === 'obligation' ? 'bg-red-100 text-red-700' :
                                            deonticType === 'permission' ? 'bg-blue-100 text-blue-700' :
                                                deonticType === 'prohibition' ? 'bg-orange-100 text-orange-700' :
                                                    'bg-gray-100 text-gray-700'
                                        }`}>
                                        {deonticType.charAt(0).toUpperCase() + deonticType.slice(1)}
                                    </span>
                                </div>
                            </div>

                            {/* Original Text Preview */}
                            <div className="mb-3">
                                <div className="text-xs font-semibold text-gray-500 mb-1">Original Text:</div>
                                <div className="text-sm text-gray-700 line-clamp-2 italic">
                                    {formula.original_text || 'N/A'}
                                </div>
                            </div>

                            {/* FOL Formula */}
                            <div>
                                <div className="text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                    <Code className="w-3 h-3 text-green-600" />
                                    FOL Expansion:
                                </div>
                                <div className="bg-gray-900 text-gray-100 p-3 rounded-lg font-mono text-xs overflow-x-auto line-clamp-2">
                                    {folFormula}
                                </div>
                            </div>

                            <div className="mt-3 text-xs text-blue-600 flex items-center gap-1">
                                <Eye className="w-3 h-3" />
                                Click to view full details
                            </div>
                        </div>
                    )
                })}
            </div>

            {filteredFormulas.length === 0 && (
                <div className="card text-center py-12">
                    <Code className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg">
                        {formulas.length === 0
                            ? 'No FOL formulas loaded from the backend'
                            : 'No formulas found matching your criteria'}
                    </p>
                </div>
            )}

            {/* Modal */}
            {selectedFormula && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedFormula(null)}>
                    <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6" onClick={e => e.stopPropagation()}>
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-2xl font-bold text-gray-800">FOL Formula Details</h2>
                            <button onClick={() => setSelectedFormula(null)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="text-sm font-semibold text-gray-700">Rule ID:</label>
                                <div className="text-gray-800 font-mono">{selectedFormula.id || 'N/A'}</div>
                            </div>

                            <div>
                                <label className="text-sm font-semibold text-gray-700">Deontic Type:</label>
                                <div>
                                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mt-1 ${selectedFormula.fol_formalization?.deontic_type === 'obligation' ? 'bg-red-100 text-red-700' :
                                            selectedFormula.fol_formalization?.deontic_type === 'permission' ? 'bg-blue-100 text-blue-700' :
                                                selectedFormula.fol_formalization?.deontic_type === 'prohibition' ? 'bg-orange-100 text-orange-700' :
                                                    'bg-gray-100 text-gray-700'
                                        }`}>
                                        {selectedFormula.fol_formalization?.deontic_type?.charAt(0).toUpperCase() + selectedFormula.fol_formalization?.deontic_type?.slice(1)}
                                    </span>
                                </div>
                            </div>

                            <div>
                                <label className="text-sm font-semibold text-gray-700 flex items-center gap-1 mb-2">
                                    <BookOpen className="w-4 h-4" />
                                    Original Policy Text:
                                </label>
                                <div className="bg-gray-50 p-4 rounded-lg text-gray-800 border border-gray-200 whitespace-pre-wrap">
                                    {selectedFormula.original_text}
                                </div>
                            </div>

                            <div>
                                <label className="text-sm font-semibold text-gray-700 mb-2 block">Deontic Formula:</label>
                                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                                    {selectedFormula.fol_formalization?.deontic_formula}
                                </div>
                            </div>

                            <div>
                                <label className="text-sm font-semibold text-gray-700 flex items-center gap-1 mb-2">
                                    <Code className="w-4 h-4 text-green-600" />
                                    FOL Expansion (Full):
                                </label>
                                <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                                    {selectedFormula.fol_formalization?.fol_expansion}
                                </div>
                            </div>

                            {selectedFormula.fol_formalization?.explanation && (
                                <div>
                                    <label className="text-sm font-semibold text-gray-700 mb-2 block">Explanation:</label>
                                    <div className="bg-blue-50 p-4 rounded-lg text-blue-900 border border-blue-200">
                                        {selectedFormula.fol_formalization.explanation}
                                    </div>
                                </div>
                            )}

                            {selectedFormula.fol_formalization?.shacl_hint && (
                                <div>
                                    <label className="text-sm font-semibold text-gray-700 mb-2 block">SHACL Hint (Phase 4):</label>
                                    <div className="bg-orange-50 p-4 rounded-lg text-orange-900 border border-orange-200 text-sm">
                                        {selectedFormula.fol_formalization.shacl_hint}
                                    </div>
                                </div>
                            )}

                            {selectedFormula.llm_classification && (
                                <div>
                                    <label className="text-sm font-semibold text-gray-700 mb-2 block">LLM Classification:</label>
                                    <div className="bg-purple-50 p-3 rounded-lg border border-purple-200 text-sm">
                                        <div><strong>Subject:</strong> {selectedFormula.llm_classification.subject || 'N/A'}</div>
                                        <div><strong>Condition:</strong> {selectedFormula.llm_classification.condition || 'None'}</div>
                                        <div><strong>Action:</strong> {selectedFormula.llm_classification.action || 'N/A'}</div>
                                        <div><strong>Deontic Marker:</strong> {selectedFormula.llm_classification.deontic_marker || 'None'}</div>
                                        <div><strong>Confidence:</strong> {(selectedFormula.llm_classification.confidence * 100).toFixed(0)}%</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
