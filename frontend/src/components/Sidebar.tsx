import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  FileCheck,
  ArrowRightLeft,
  Wallet,
  Network,
  Cpu,
  HelpCircle,
  GitBranch,
  ShieldAlert,
  Blocks,
  FileText,
  Sliders,
  History,
  FileBarChart,
  Settings as SettingsIcon
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/cases', label: 'Case Management', icon: Briefcase },
  { path: '/evidence', label: 'Evidence Repository', icon: FileCheck },
  { path: '/transactions', label: 'Transaction Triage', icon: ArrowRightLeft },
  { path: '/wallets', label: 'Wallet Intelligence', icon: Wallet },
  { path: '/investigation/graph', label: 'Investigation Graph', icon: Network },
  { path: '/ai-analysis', label: 'AI Risk Scoring', icon: Cpu },
  { path: '/explanations', label: 'SHAP Explainability', icon: HelpCircle },
  { path: '/chain-of-custody', label: 'Chain of Custody', icon: GitBranch },
  { path: '/integrity', label: 'Integrity & Tamper', icon: ShieldAlert },
  { path: '/blockchain', label: 'Blockchain Anchor', icon: Blocks },
  { path: '/models', label: 'Model Governance', icon: Sliders },
  { path: '/evaluation', label: 'Evaluation & Ablation', icon: FileBarChart },
  { path: '/audit', label: 'Audit Trail', icon: History },
  { path: '/reports', label: 'Forensic Reports', icon: FileText },
  { path: '/settings', label: 'Settings', icon: SettingsIcon },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-60 bg-navy-900 border-r border-forensic-border flex flex-col h-[calc(100vh-3.5rem)] sticky top-14">
      {/* Five Trust Dimensions Indicator */}
      <div className="p-3 border-b border-forensic-border/60 bg-slate-950/40">
        <div className="text-[10px] uppercase font-mono font-bold tracking-wider text-slate-400 mb-1.5">
          5 Trust Dimensions
        </div>
        <div className="grid grid-cols-5 gap-1 text-center">
          <div className="text-[9px] font-mono py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800" title="Evidence Trust">EVI</div>
          <div className="text-[9px] font-mono py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800" title="Analytical Trust">ANA</div>
          <div className="text-[9px] font-mono py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800" title="Explanatory Trust">EXP</div>
          <div className="text-[9px] font-mono py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800" title="Governance Trust">GOV</div>
          <div className="text-[9px] font-mono py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800" title="Legal Trust">LEG</div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold shadow-sm shadow-blue-950'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer System State */}
      <div className="p-3 border-t border-forensic-border/60 bg-slate-950/40 text-[10px] font-mono text-slate-400">
        <div className="flex justify-between items-center mb-1">
          <span>PIPELINE STATE:</span>
          <span className="text-emerald-400 font-bold">ACTIVE</span>
        </div>
        <div className="flex justify-between items-center text-slate-400">
          <span>LEAKAGE GUARD:</span>
          <span className="text-blue-400">ENFORCED</span>
        </div>
      </div>
    </aside>
  );
};
