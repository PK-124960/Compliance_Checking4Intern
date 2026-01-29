import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard,
    FileText,
    Code,
    Shield,
    ChevronLeft,
    ChevronRight,
    Sparkles,
    Play,
    Brain
} from 'lucide-react'

const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/rules', icon: FileText, label: 'Rules' },
    { path: '/fol', icon: Code, label: 'FOL Viewer' },
    { path: '/validation', icon: Shield, label: 'Validation' },
    { path: '/demo', icon: Play, label: 'Live Demo' },
    { path: '/agent', icon: Brain, label: 'Agentic System' },
]

export default function Sidebar({ open, setOpen }) {
    return (
        <aside className={`fixed left-0 top-0 h-screen bg-white border-r border-slate-200 transition-all duration-300 z-50 shadow-sm ${open ? 'w-64' : 'w-20'}`}>
            {/* Logo */}
            <div className="flex items-center gap-3 p-6 border-b border-slate-100">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                    <Sparkles className="w-5 h-5 text-white" />
                </div>
                {open && (
                    <div>
                        <h1 className="font-bold text-lg text-slate-800">PolicyChecker</h1>
                        <p className="text-xs text-slate-500">AI Policy Formalization</p>
                    </div>
                )}
            </div>

            {/* Navigation */}
            <nav className="p-4 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                                ? 'bg-blue-50 text-blue-600 font-semibold'
                                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                            }`
                        }
                    >
                        <item.icon className="w-5 h-5 flex-shrink-0" />
                        {open && <span className="font-medium">{item.label}</span>}
                    </NavLink>
                ))}
            </nav>

            {/* Toggle button */}
            <button
                onClick={() => setOpen(!open)}
                className="absolute bottom-6 right-[-12px] w-6 h-6 bg-white border border-slate-200 shadow-sm rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors"
            >
                {open ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
        </aside>
    )
}
