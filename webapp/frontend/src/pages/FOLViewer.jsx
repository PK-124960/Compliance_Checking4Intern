import { useState, useEffect } from 'react'
import { Search, Code, Filter, Sparkles, FileText } from 'lucide-react'
import axios from 'axios'

export default function FOLViewer() {
    const [folData, setFolData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [searchTerm, setSearchTerm] = useState('')
    const [filterType, setFilterType] = useState('All')

    useEffect(() => {
        fetchFOLData()
    }, [])

    const fetchFOLData = async () => {
        try {
            const res = await axios.get('/api/fol')
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

    const filteredFormulas = formulas.filter(f => {
        const deonticType = f.fol_formalization?.deontic_type || ''
        const ruleId = f.id || ''
        const originalText = f.original_text || ''
        const folExpansion = f.fol_formalization?.fol_expansion || ''

        const matchesSearch = ruleId.toLowerCase().includes(searchTerm.toLowerCase()) ||
            originalText.toLowerCase().includes(searchTerm.toLowerCase()) ||
            folExpansion.toLowerCase().includes(searchTerm.toLowerCase())

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
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            <Filter className="w-4 h-4 inline mr-1" />
                            Filter by Type
                        </label>
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

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <div className="card text-center bg-gray-50">
                    <div className="text-3xl font-bold text-gray-700">{filteredFormulas.length}</div>
                    <div className="text-sm text-gray-600 mt-1">Showing</div>
                </div>
                <div className="card text-center bg-red-50">
                    <div className="text-3xl font-bold text-red-600">{typeCounts.Obligation}</div>
                    <div className="text-sm text-red-600 mt-1 font-medium">Obligations</div>
                </div>
                <div className="card text-center bg-green-50">
                    <div className="text-3xl font-bold text-green-600">{typeCounts.Permission}</div>
                    <div className="text-sm text-green-600 mt-1 font-medium">Permissions</div>
                </div>
                <div className="card text-center bg-orange-50">
                    <div className="text-3xl font-bold text-orange-600">{typeCounts.Prohibition}</div>
                    <div className="text-sm text-orange-600 mt-1 font-medium">Prohibitions</div>
                </div>
            </div>

            {/* Research Finding */}
            <div className="card bg-gradient-to-r from-green-50 to-green-100 border-l-4 border-green-500">
                <h3 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
                    <Code className="w-5 h-5" />
                    Research Finding (RQ2)
                </h3>
                <p className="text-green-700">
                    <strong>FOL is sufficient</strong> for institutional policy formalization. No higher-order logic required.
                </p>
            </div>

            {/* Formulas List - MATCHING RULES BROWSER PATTERN */}
            <div className="space-y-4">
                {filteredFormulas.map((formula, idx) => {
                    const deonticType = formula.fol_formalization?.deontic_type || 'Unknown'
                    const ruleId = formula.id || `F${idx + 1}`
                    const originalText = formula.original_text || 'No text available'
                    const simplifiedText = originalText.replace(/\n/g, ' ')
                    const deonticFormula = formula.fol_formalization?.deontic_formula || 'N/A'
                    const folExpansion = formula.fol_formalization?.fol_expansion || 'N/A'
                    const explanation = formula.fol_formalization?.explanation
                    const shaclHint = formula.fol_formalization?.shacl_hint

                    return (
                        <div key={idx} className="card hover:shadow-xl transition-all">
                            <div className="flex items-start gap-4">
                                <div className="flex-shrink-0">
                                    <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center text-white shadow-lg">
                                        <div className="text-center">
                                            <div className="text-xs font-semibold">{ruleId}</div>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex-1">
                                    {/* Type Badge */}
                                    <div className="flex items-center gap-2 mb-3 flex-wrap">
                                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${deonticType.toLowerCase() === 'obligation' ? 'bg-red-100 text-red-700' :
                                            deonticType.toLowerCase() === 'permission' ? 'bg-green-100 text-green-700' :
                                                deonticType.toLowerCase() === 'prohibition' ? 'bg-orange-100 text-orange-700' :
                                                    'bg-gray-100 text-gray-700'
                                            }`}>
                                            {deonticType.charAt(0).toUpperCase() + deonticType.slice(1)}
                                        </span>
                                    </div>

                                    {/* Original Text */}
                                    <div className="mb-3">
                                        <div className="text-xs font-semibold text-gray-500 mb-1 flex items-center gap-1">
                                            <FileText className="w-3 h-3" />
                                            Original Policy Text:
                                        </div>
                                        <div className="bg-gray-50 p-3 rounded border border-gray-200 text-gray-600 text-sm italic whitespace-pre-wrap">
                                            {originalText}
                                        </div>
                                    </div>

                                    {/* Simplified Text */}
                                    <div className="mb-3">
                                        <div className="text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                            <Sparkles className="w-3 h-3 text-blue-600" />
                                            Simplified (Phase 1):
                                        </div>
                                        <p className="text-gray-800 leading-relaxed text-base font-medium">
                                            {simplifiedText}
                                        </p>
                                    </div>

                                    {/* Deontic Formula */}
                                    <div className="mb-3">
                                        <div className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
                                            <Code className="w-3 h-3 text-purple-600" />
                                            Deontic Formula (Symbolic):
                                        </div>
                                        <div className="bg-purple-900 text-purple-100 p-3 rounded-lg font-mono text-sm overflow-x-auto">
                                            {deonticFormula}
                                        </div>
                                    </div>

                                    {/* FOL Expansion */}
                                    <div className="mb-3">
                                        <div className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
                                            <Code className="w-3 h-3 text-green-600" />
                                            FOL Expansion (Full First-Order Logic):
                                        </div>
                                        <div className="bg-gray-900 text-gray-100 p-3 rounded-lg font-mono text-sm overflow-x-auto">
                                            {folExpansion}
                                        </div>
                                    </div>

                                    {/* Explanation */}
                                    {explanation && (
                                        <div className="mb-3">
                                            <div className="text-xs font-semibold text-gray-700 mb-1">
                                                Explanation:
                                            </div>
                                            <p className="text-gray-700 text-sm italic bg-blue-50 p-3 rounded border border-blue-200">
                                                {explanation}
                                            </p>
                                        </div>
                                    )}

                                    {/* SHACL Hint */}
                                    {shaclHint && (
                                        <div className="mt-3">
                                            <div className="text-xs font-semibold text-gray-700 mb-1 flex items-center gap-1">
                                                <Code className="w-3 h-3 text-orange-600" />
                                                SHACL Hint (for Phase 4):
                                            </div>
                                            <div className="bg-orange-50 p-3 rounded border border-orange-200 text-orange-900 text-sm font-mono">
                                                {shaclHint}
                                            </div>
                                        </div>
                                    )}
                                </div>
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
                    {formulas.length === 0 && (
                        <p className="text-sm text-gray-400 mt-2">
                            Check that the backend is running and the API endpoint is accessible
                        </p>
                    )}
                </div>
            )}
        </div>
    )
}
