import React from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, ShieldAlert, Cpu, Database, UserCheck, Terminal } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, switchRole } = useAuth();

  return (
    <header className="h-14 bg-navy-900 border-b border-forensic-border px-4 flex items-center justify-between sticky top-0 z-30">
      {/* Brand & System Tagline */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-blue-600/20 border border-blue-500/50 flex items-center justify-center text-blue-400 font-mono font-bold text-sm">
            FX
          </div>
          <div>
            <span className="font-bold tracking-tight text-white text-sm font-mono">TCF-FX</span>
            <span className="text-[10px] text-blue-400 font-mono ml-2 border border-blue-900/60 bg-blue-950/40 px-1.5 py-0.5 rounded">
              v1.0.0 RESEARCH-GRADE
            </span>
          </div>
        </div>
        <div className="hidden lg:block h-4 w-[1px] bg-slate-800" />
        <span className="hidden lg:block text-xs text-slate-400 italic">
          "Evidence-aware AI for explainable cryptocurrency investigations."
        </span>
      </div>

      {/* Forensic Axiom Badge */}
      <div className="hidden xl:flex items-center gap-1.5 px-3 py-1 bg-slate-900/80 border border-slate-800 rounded text-[11px] font-mono text-slate-300">
        <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
        <span>AI Output &ne; Forensic Finding &ne; Legal Conclusion</span>
      </div>

      {/* Right Controls: Role Switcher & User Profile */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded px-2 py-1">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">Role:</span>
          <select
            value={user.role}
            onChange={(e) => switchRole(e.target.value as any)}
            className="bg-transparent text-xs font-mono font-semibold text-blue-400 focus:outline-none cursor-pointer"
          >
            <option value="ADMIN" className="bg-slate-900">ADMIN</option>
            <option value="INVESTIGATOR" className="bg-slate-900">INVESTIGATOR</option>
            <option value="ANALYST" className="bg-slate-900">ANALYST</option>
            <option value="AUDITOR" className="bg-slate-900">AUDITOR</option>
            <option value="VIEWER" className="bg-slate-900">VIEWER</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200">
            {user.username.slice(0, 2).toUpperCase()}
          </div>
          <div className="hidden sm:block text-left leading-tight">
            <div className="text-xs font-medium text-slate-200">{user.username}</div>
            <div className="text-[10px] text-slate-400 font-mono">{user.role}</div>
          </div>
        </div>
      </div>
    </header>
  );
};
