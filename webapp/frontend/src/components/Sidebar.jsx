import { NavLink } from 'react-router-dom'
import { Home, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react'
export default function Sidebar({ open, setOpen }) {
    return (
        <aside className={`fixed left-0 top-0 h-screen bg-white border-r transition-all ${open ? 'w-72' : 'w-20'}`}>
            <div className="flex items-center gap-3 p-6 border-b">
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-white" />
                </div>
                {open && <h1 className="font-bold">PolicyChecker</h1>}
            </div>
            <nav className="p-4">
                <NavLink to="/" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-50 text-blue-700">
                    <Home className="w-5 h-5" />
                    {open && <span>Research Overview</span>}
                </NavLink>
            </nav>
            <button onClick={() => setOpen(!open)} className="absolute bottom-24 right-[-12px] w-6 h-6 bg-white border rounded-full">
                {open ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
        </aside>
    )
}
