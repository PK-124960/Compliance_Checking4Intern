export default function Dashboard() {
    return (
        <div className="space-y-8">
            <div className="card bg-gradient-to-br from-blue-50 to-white p-12 text-center">
                <h1 className="text-5xl font-bold mb-3">Automated Policy Formalization Pipeline</h1>
                <p className="text-xl text-gray-600">From Natural Language to Semantic Web Constraints</p>
            </div>
            <div className="grid grid-cols-4 gap-4">
                <div className="card text-center"><div className="text-4xl font-bold text-blue-600">97</div><div className="text-sm text-gray-600 mt-2">Total Rules</div></div>
                <div className="card text-center"><div className="text-4xl font-bold text-purple-600">99%</div><div className="text-sm text-gray-600 mt-2">Classification</div></div>
                <div className="card text-center"><div className="text-4xl font-bold text-green-600">97</div><div className="text-sm text-gray-600 mt-2">FOL Formalized</div></div>
                <div className="card text-center"><div className="text-4xl font-bold text-orange-600">1,309</div><div className="text-sm text-gray-600 mt-2">SHACL Triples</div></div>
            </div>
        </div>
    )
}
