import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { DashboardSummary } from '../types';
import { RiskBadge, IntegrityBadge } from '../components/RiskBadge';
import { Link } from 'react-router-dom';
import {
  Briefcase,
  ShieldCheck,
  ShieldAlert,
  Cpu,
  Layers,
  Activity,
  ArrowRight,
  TrendingUp,
  FileCheck,
  Blocks,
  Filter
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dashboard/summary');
      setSummary(res.data);
    } catch (err) {
      console.error('Failed to load dashboard summary', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-full text-slate-400 font-mono text-xs">
        <Activity className="w-5 h-5 animate-spin mr-2 text-blue-400" />
        LOADING FORENSIC INTELLIGENCE DASHBOARD...
      </div>
    );
  }

  const m = summary?.metrics;
  const dist = summary?.risk_distribution;

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-400" />
            FORENSIC INTELLIGENCE DASHBOARD
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Real-time cryptocurrency risk triage, temporal graph state, and cryptographic chain of custody.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/cases"
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold flex items-center gap-1.5 shadow-sm shadow-blue-950 transition-colors"
          >
            <Briefcase className="w-3.5 h-3.5" />
            Cases
          </Link>
          <Link
            to="/investigation/graph"
            className="px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors"
          >
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            Graph Explorer
          </Link>
        </div>
      </div>

      {/* 6 Key Operational KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <div className="text-[10px] text-slate-400 uppercase">Active Cases</div>
          <div className="text-2xl font-bold text-white mt-1">{m?.open_cases || 0}</div>
          <div className="text-[10px] text-blue-400 mt-1 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" /> Isolated
          </div>
        </div>

        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <div className="text-[10px] text-slate-400 uppercase">Evidence Ingested</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">{m?.total_evidence || 0}</div>
          <div className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">
            <ShieldCheck className="w-3 h-3" /> SHA-256 Hashed
          </div>
        </div>

        <div className="bg-navy-900 border border-red-950/80 p-4 rounded-lg bg-gradient-to-b from-red-950/20 to-transparent">
          <div className="text-[10px] text-red-400 uppercase font-semibold">Critical Leads</div>
          <div className="text-2xl font-bold text-red-400 mt-1">{m?.critical_leads || 0}</div>
          <div className="text-[10px] text-red-400/80 mt-1">Priority Triage 1</div>
        </div>

        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <div className="text-[10px] text-slate-400 uppercase">Review Queue</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{m?.analyst_review_queue || 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Pending Human Review</div>
        </div>

        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <div className="text-[10px] text-slate-400 uppercase">Confirmed Findings</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">{m?.confirmed_findings || 0}</div>
          <div className="text-[10px] text-purple-300/80 mt-1">Analyst Promoted</div>
        </div>

        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <div className="text-[10px] text-slate-400 uppercase">Blockchain Anchors</div>
          <div className="text-2xl font-bold text-blue-400 mt-1">{m?.anchored_on_chain || 0}</div>
          <div className="text-[10px] text-blue-300/80 mt-1">On-Chain Proofs</div>
        </div>
      </div>

      {/* Analytics & Risk Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Breakdown */}
        <div className="bg-navy-900 border border-forensic-border p-5 rounded-lg">
          <h2 className="text-xs font-bold uppercase text-slate-300 mb-4 flex items-center justify-between">
            <span>Investigative Risk Distribution</span>
            <span className="text-[10px] text-slate-400 font-normal">N = {m?.total_evidence || 0}</span>
          </h2>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-red-400 font-semibold">CRITICAL RISK (&ge; 0.80)</span>
                <span className="text-slate-200">{dist?.critical || 0} items</span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-red-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${((dist?.critical || 0) / Math.max(1, m?.total_evidence || 1)) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-orange-400 font-semibold">HIGH RISK (0.60 - 0.79)</span>
                <span className="text-slate-200">{dist?.high || 0} items</span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-orange-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${((dist?.high || 0) / Math.max(1, m?.total_evidence || 1)) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-yellow-400 font-semibold">MEDIUM RISK (0.35 - 0.59)</span>
                <span className="text-slate-200">{dist?.medium || 0} items</span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-yellow-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${((dist?.medium || 0) / Math.max(1, m?.total_evidence || 1)) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-emerald-400 font-semibold">LOW / ROUTINE (&lt; 0.35)</span>
                <span className="text-slate-200">{dist?.low || 0} items</span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${((dist?.low || 0) / Math.max(1, m?.total_evidence || 1)) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Multi-Model Analytical Stack Status */}
        <div className="bg-navy-900 border border-forensic-border p-5 rounded-lg lg:col-span-2">
          <h2 className="text-xs font-bold uppercase text-slate-300 mb-4 flex items-center justify-between">
            <span>Analytical Engine Registry & Status</span>
            <span className="text-[10px] text-emerald-400">ENGINES SYNCHRONIZED</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-xs font-bold text-white">Paper Baseline Random Forest</div>
                  <div className="text-[10px] text-slate-400">250 Trees &bull; Depth 12 &bull; Balanced</div>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">ACTIVE</span>
              </div>
              <div className="mt-2 text-[11px] text-slate-300 flex justify-between">
                <span>F1-Score: 0.884</span>
                <span>ROC-AUC: 0.942</span>
              </div>
            </div>

            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-xs font-bold text-white">Isolation Forest Anomaly</div>
                  <div className="text-[10px] text-slate-400">150 Trees &bull; Contamination 0.08</div>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">ACTIVE</span>
              </div>
              <div className="mt-2 text-[11px] text-slate-300 flex justify-between">
                <span>Unsupervised Ranker</span>
                <span className="text-blue-400">Topological Outlier</span>
              </div>
            </div>

            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-xs font-bold text-white">SHAP TreeExplainer</div>
                  <div className="text-[10px] text-slate-400">Local Decision Driver Attributions</div>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-purple-950 text-purple-400 border border-purple-800">ONLINE</span>
              </div>
              <div className="mt-2 text-[11px] text-slate-300 flex justify-between">
                <span>Evidence-Bound Drivers</span>
                <span className="text-purple-300">&plusmn; Impact</span>
              </div>
            </div>

            <div className="p-3 bg-slate-950 rounded border border-slate-800">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-xs font-bold text-white">Temporal Graph Engine</div>
                  <div className="text-[10px] text-slate-400">G(t-) Anti-Leakage Invariants</div>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-blue-950 text-blue-400 border border-blue-800">ENFORCED</span>
              </div>
              <div className="mt-2 text-[11px] text-slate-300 flex justify-between">
                <span>Velocity &bull; Clustering &bull; Exposure</span>
                <span className="text-emerald-400">Zero Leakage</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Priority Leads Table */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <div className="p-4 border-b border-forensic-border flex justify-between items-center bg-slate-950/40">
          <div>
            <h2 className="text-xs font-bold uppercase text-slate-200">High-Priority Forensic Triage Leads</h2>
            <p className="text-[11px] text-slate-400 font-sans">Algorithmic risk output pending independent human corroboration</p>
          </div>
          <Link
            to="/evidence"
            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            All Evidence <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
              <tr>
                <th className="py-2.5 px-4">Evidence ID</th>
                <th className="py-2.5 px-4">Transaction ID</th>
                <th className="py-2.5 px-4">Amount</th>
                <th className="py-2.5 px-4">Forensic Risk</th>
                <th className="py-2.5 px-4">Uncertainty</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Integrity Digest</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {summary?.recent_leads?.map((lead) => (
                <tr key={lead.evidence_id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 px-4 text-blue-400 font-bold">
                    <Link to={`/evidence/${lead.evidence_id}`}>{lead.evidence_id}</Link>
                  </td>
                  <td className="py-2.5 px-4 text-slate-300">{lead.transaction_id}</td>
                  <td className="py-2.5 px-4 text-white font-bold">{lead.amount.toFixed(2)} BTC</td>
                  <td className="py-2.5 px-4">
                    <RiskBadge score={lead.risk_score} />
                  </td>
                  <td className="py-2.5 px-4 text-slate-400">&plusmn;{lead.uncertainty_delta?.toFixed(2)}</td>
                  <td className="py-2.5 px-4">
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                      {lead.analyst_status}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">
                    <IntegrityBadge isTampered={lead.is_tampered} isAnchored={lead.is_anchored} />
                  </td>
                  <td className="py-2.5 px-4 text-right">
                    <Link
                      to={`/evidence/${lead.evidence_id}`}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] border border-slate-700 inline-flex items-center gap-1"
                    >
                      Inspect <ArrowRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))}
              {(!summary?.recent_leads || summary.recent_leads.length === 0) && (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400 text-xs">
                    No evidence records ingested yet. Run <code className="text-blue-400">tcf demo</code> to ingest transactions.
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
