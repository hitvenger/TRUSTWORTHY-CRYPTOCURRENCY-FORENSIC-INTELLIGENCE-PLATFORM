import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings as SettingsIcon, ShieldCheck, UserCheck, Database, HardDrive, Key } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { user, switchRole } = useAuth();

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="border-b border-forensic-border pb-4">
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-blue-400" />
          SYSTEM CONFIGURATION & ACCESS CONTROL
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-sans">
          Role-Based Access Control (RBAC), storage engine configuration, and cryptographic parameter registry.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* User Identity & Role Control */}
        <div className="bg-navy-900 border border-forensic-border rounded-lg p-5 space-y-4">
          <h2 className="text-xs font-bold uppercase text-slate-200 flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-blue-400" /> Active Session & RBAC Role
          </h2>

          <div className="space-y-3 bg-slate-950 p-4 rounded border border-slate-800">
            <div>
              <span className="text-slate-400 block text-[10px]">CURRENT USER</span>
              <span className="text-white font-bold">{user.username}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">EMAIL IDENTIFIER</span>
              <span className="text-slate-300">{user.email}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] mb-1">SWITCH ROLE (DEMO / SIMULATION)</span>
              <select
                value={user.role}
                onChange={(e) => switchRole(e.target.value as any)}
                className="w-full bg-slate-900 border border-slate-800 text-blue-400 rounded px-3 py-2 font-bold focus:outline-none"
              >
                <option value="ADMIN">ADMIN (Full Administrative Control)</option>
                <option value="INVESTIGATOR">INVESTIGATOR (Case Creation & Evidence Ingestion)</option>
                <option value="ANALYST">ANALYST (Triage Review & Findings Promotion)</option>
                <option value="AUDITOR">AUDITOR (Read-Only Chained Custody & Integrity Inspection)</option>
                <option value="VIEWER">VIEWER (Read-Only Public Dashboard)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Security & Cryptographic Settings */}
        <div className="bg-navy-900 border border-forensic-border rounded-lg p-5 space-y-4">
          <h2 className="text-xs font-bold uppercase text-slate-200 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> Cryptographic Parameters
          </h2>

          <div className="space-y-3 bg-slate-950 p-4 rounded border border-slate-800 font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">HASH ALGORITHM:</span>
              <span className="text-white font-bold">SHA-256 (Canonical JSON)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">CHAIN LINKAGE:</span>
              <span className="text-emerald-400 font-bold">Continuous Chained Hash</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">TEMPORAL LEAK GUARD:</span>
              <span className="text-blue-400 font-bold">G(t-) Anti-Leakage Assertions</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">BLOCKCHAIN ANCHOR:</span>
              <span className="text-purple-400 font-bold">EVM EvidenceAnchor.sol</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
