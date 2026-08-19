import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { EvidenceItem } from '../types';
import { RiskBadge, IntegrityBadge } from '../components/RiskBadge';
import { Link } from 'react-router-dom';
import { FileCheck, Search, Filter, ShieldAlert, ArrowRight, Activity, ShieldCheck } from 'lucide-react';

export const EvidencePage: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterRisk, setFilterRisk] = useState<string>('ALL');

  useEffect(() => {
    fetchEvidence();
  }, []);

  const fetchEvidence = async () => {
    try {
      setLoading(true);
      // Fetch all cases first, then collect evidence items or query dashboard leads
      const res = await api.get('/dashboard/summary');
      if (res.data?.recent_leads) {
        setEvidenceList(res.data.recent_leads);
      }
    } catch (err) {
      console.error('Failed to load evidence repository', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = evidenceList.filter((item) => {
    const matchesSearch =
      item.evidence_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.integrity_digest.toLowerCase().includes(searchTerm.toLowerCase());

    if (filterRisk === 'CRITICAL') return matchesSearch && item.risk_score >= 0.8;
    if (filterRisk === 'HIGH') return matchesSearch && item.risk_score >= 0.6;
    if (filterRisk === 'TAMPERED') return matchesSearch && item.is_tampered;
    return matchesSearch;
  });

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-blue-400" />
            DIGITAL EVIDENCE INVENTORY
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Cryptographically preserved cryptocurrency evidence records with canonical SHA-256 digests and provenance lineages.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between bg-navy-900 border border-forensic-border p-3 rounded-lg">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by Evidence ID, Transaction ID, or SHA-256 Digest..."
            className="w-full bg-slate-950 border border-slate-800 rounded pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded px-3 py-1.5 focus:outline-none focus:border-blue-500"
          >
            <option value="ALL">All Evidence Items</option>
            <option value="CRITICAL">Critical Risk Only (&ge; 0.80)</option>
            <option value="HIGH">High Risk Only (&ge; 0.60)</option>
            <option value="TAMPERED">Tampered Items Only</option>
          </select>
        </div>
      </div>

      {/* Evidence Table */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
              <tr>
                <th className="py-2.5 px-4">Evidence ID</th>
                <th className="py-2.5 px-4">Case ID</th>
                <th className="py-2.5 px-4">Transaction ID</th>
                <th className="py-2.5 px-4">Amount</th>
                <th className="py-2.5 px-4">Risk / Confidence</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Cryptographic Digest</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((item) => (
                <tr key={item.evidence_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-4 text-blue-400 font-bold">
                    <Link to={`/evidence/${item.evidence_id}`}>{item.evidence_id}</Link>
                  </td>
                  <td className="py-2.5 px-4 text-slate-300">
                    <Link to={`/cases/${item.case_id}`} className="hover:underline">{item.case_id}</Link>
                  </td>
                  <td className="py-2.5 px-4 text-slate-300">{item.transaction_id}</td>
                  <td className="py-2.5 px-4 text-white font-bold">{item.amount?.toFixed(2)} BTC</td>
                  <td className="py-2.5 px-4">
                    <RiskBadge score={item.risk_score} />
                    <span className="text-[10px] text-slate-400 ml-1.5">&plusmn;{item.uncertainty_delta?.toFixed(2)}</span>
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                      {item.analyst_status}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">
                    <IntegrityBadge isTampered={item.is_tampered} isAnchored={item.is_anchored} />
                  </td>
                  <td className="py-2.5 px-4 text-right">
                    <Link
                      to={`/evidence/${item.evidence_id}`}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] border border-slate-700"
                    >
                      Inspect
                    </Link>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && !loading && (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400 text-xs">
                    No evidence records match the current filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
