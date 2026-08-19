import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Case } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { Link } from 'react-router-dom';
import { Briefcase, Plus, Search, Filter, FolderPlus, ArrowRight, ShieldCheck } from 'lucide-react';

export const CasesPage: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [newTitle, setNewTitle] = useState<string>('');
  const [newDesc, setNewDesc] = useState<string>('');
  const [newInvestigator, setNewInvestigator] = useState<string>('Special Agent Vance');
  const [newPriority, setNewPriority] = useState<string>('HIGH');

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const res = await api.get('/cases');
      setCases(res.data);
    } catch (err) {
      console.error('Failed to load cases', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;
    try {
      await api.post('/cases', {
        title: newTitle,
        description: newDesc,
        investigator: newInvestigator,
        priority: newPriority,
        tags: ['FORENSIC_INVESTIGATION', 'CRYPTO'],
      });
      setShowModal(false);
      setNewTitle('');
      setNewDesc('');
      fetchCases();
    } catch (err) {
      console.error('Failed to create case', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white font-mono tracking-tight flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-blue-400" />
            CASE MANAGEMENT REPOSITORY
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Auditable digital forensics investigation cases with strict cryptographic isolation and chained custody.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold font-mono flex items-center gap-2 shadow-sm shadow-blue-950"
        >
          <Plus className="w-4 h-4" />
          Initialize New Case
        </button>
      </div>

      {/* Case Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {cases.map((c) => (
          <div
            key={c.case_id}
            className="bg-navy-900 border border-forensic-border rounded-lg p-5 flex flex-col justify-between hover:border-blue-500/40 transition-colors"
          >
            <div>
              <div className="flex justify-between items-start mb-2">
                <span className="text-[11px] font-mono text-blue-400 font-bold tracking-wider">{c.case_id}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${
                  c.status === 'ACTIVE' ? 'bg-emerald-950/70 text-emerald-400 border-emerald-800' : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}>
                  {c.status}
                </span>
              </div>

              <h2 className="text-sm font-bold text-white mb-2 leading-snug">{c.title}</h2>
              <p className="text-xs text-slate-400 line-clamp-2 mb-4">{c.description || 'No case description provided.'}</p>
            </div>

            <div className="pt-4 border-t border-forensic-border/60">
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-300 mb-4 bg-slate-950 p-2.5 rounded border border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[10px]">LEAD INVESTIGATOR</span>
                  <span className="truncate block font-semibold">{c.investigator}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">EVIDENCE COUNT</span>
                  <span className="text-blue-400 font-bold">{c.evidence_count || 0} items</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <RiskBadge level={c.priority} />
                <Link
                  to={`/cases/${c.case_id}`}
                  className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono font-medium flex items-center gap-1 border border-slate-700"
                >
                  Open Case <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          </div>
        ))}

        {cases.length === 0 && !loading && (
          <div className="col-span-full py-12 text-center text-slate-400 font-mono text-xs">
            No forensic cases found. Click "Initialize New Case" to begin an investigation.
          </div>
        )}
      </div>

      {/* Create Case Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-navy-900 border border-forensic-border rounded-lg max-w-md w-full p-6 shadow-2xl">
            <h2 className="text-sm font-bold text-white font-mono uppercase mb-4 flex items-center gap-2">
              <FolderPlus className="w-4 h-4 text-blue-400" />
              Initialize Forensic Investigation Case
            </h2>

            <form onSubmit={handleCreateCase} className="space-y-4 font-mono text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Case Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Operation ShadowMixer Investigation"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 font-sans"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Investigation Objective / Description</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Describe investigative scope, targeted addresses, and jurisdiction..."
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 font-sans h-20"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Lead Investigator</label>
                  <input
                    type="text"
                    value={newInvestigator}
                    onChange={(e) => setNewInvestigator(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Priority</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-forensic-border">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold"
                >
                  Create & Record Genesis Event
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
