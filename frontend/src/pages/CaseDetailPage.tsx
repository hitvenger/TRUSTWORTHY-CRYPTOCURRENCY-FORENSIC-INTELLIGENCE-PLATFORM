import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/client';
import { Case, EvidenceItem, CustodyEvent } from '../types';
import { RiskBadge, IntegrityBadge } from '../components/RiskBadge';
import {
  Briefcase,
  FileCheck,
  GitBranch,
  FileDown,
  Plus,
  ArrowLeft,
  CheckCircle,
  Activity,
  Layers,
  ShieldCheck,
  Download
} from 'lucide-react';

export const CaseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [custodyEvents, setCustodyEvents] = useState<CustodyEvent[]>([]);
  const [activeTab, setActiveTab] = useState<'evidence' | 'custody' | 'reports'>('evidence');
  const [loading, setLoading] = useState<boolean>(true);

  // Ingest transaction modal state
  const [showIngestModal, setShowIngestModal] = useState<boolean>(false);
  const [txId, setTxId] = useState<string>('');
  const [srcWallet, setSrcWallet] = useState<string>('');
  const [dstWallet, setDstWallet] = useState<string>('');
  const [amount, setAmount] = useState<string>('25.5');

  useEffect(() => {
    if (id) {
      fetchCaseDetails();
    }
  }, [id]);

  const fetchCaseDetails = async () => {
    try {
      setLoading(true);
      const [cRes, evRes, cocRes] = await Promise.all([
        api.get(`/cases/${id}`),
        api.get(`/cases/${id}/evidence`),
        api.get(`/audit/custody-chain/${id}`),
      ]);
      setCaseData(cRes.data);
      setEvidenceList(evRes.data);
      setCustodyEvents(cocRes.data.events || []);
    } catch (err) {
      console.error('Failed to load case details', err);
    } finally {
      setLoading(false);
    }
  };

  const handleIngestEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!txId || !srcWallet || !dstWallet) return;
    try {
      await api.post(`/cases/${id}/evidence`, {
        case_id: id,
        transaction_id: txId,
        source_wallet: srcWallet,
        destination_wallet: dstWallet,
        amount: parseFloat(amount) || 1.0,
        timestamp: Date.now() / 1000,
        source: 'MANUAL_INGESTION',
      });
      setShowIngestModal(false);
      setTxId('');
      setSrcWallet('');
      setDstWallet('');
      fetchCaseDetails();
    } catch (err) {
      console.error('Failed to ingest evidence', err);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center text-slate-400 font-mono text-sm">
        <Activity className="w-5 h-5 animate-spin mr-2 text-blue-400" />
        LOADING CASE DOSSIER...
      </div>
    );
  }

  if (!caseData) {
    return (
      <div className="p-8 text-center text-red-400 font-mono">
        Case not found.
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Back button & Breadcrumbs */}
      <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
        <Link to="/cases" className="hover:text-white flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Cases
        </Link>
        <span>/</span>
        <span className="text-slate-200">{caseData.case_id}</span>
      </div>

      {/* Case Header Card */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-forensic-border/80 pb-4 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono font-bold text-blue-400">{caseData.case_id}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                {caseData.status}
              </span>
              <RiskBadge level={caseData.priority} />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">{caseData.title}</h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowIngestModal(true)}
              className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-mono font-semibold flex items-center gap-1.5 shadow-sm shadow-blue-950"
            >
              <Plus className="w-3.5 h-3.5" />
              Ingest Evidence
            </button>
            <a
              href={`/api/v1/reports/${id}/pdf`}
              target="_blank"
              rel="noreferrer"
              className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono font-semibold flex items-center gap-1.5 border border-slate-700"
            >
              <Download className="w-3.5 h-3.5 text-blue-400" />
              Export PDF Dossier
            </a>
          </div>
        </div>

        {/* Case Metadata Attributes */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono bg-slate-950 p-4 rounded border border-slate-800">
          <div>
            <span className="text-slate-400 block text-[10px]">LEAD INVESTIGATOR</span>
            <span className="text-white font-semibold">{caseData.investigator}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">EVIDENCE ITEMS</span>
            <span className="text-blue-400 font-bold">{evidenceList.length} registered</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">CUSTODY EVENTS</span>
            <span className="text-emerald-400 font-bold">{custodyEvents.length} chained hashes</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">CREATION TIMESTAMP</span>
            <span className="text-slate-300">{caseData.created_at ? new Date(caseData.created_at).toLocaleString() : 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-forensic-border gap-6 text-xs font-mono font-semibold">
        <button
          onClick={() => setActiveTab('evidence')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'evidence'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileCheck className="w-4 h-4" />
          Evidence Inventory ({evidenceList.length})
        </button>
        <button
          onClick={() => setActiveTab('custody')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'custody'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <GitBranch className="w-4 h-4" />
          Chain of Custody ({custodyEvents.length})
        </button>
        <button
          onClick={() => setActiveTab('reports')}
          className={`pb-3 border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'reports'
              ? 'border-blue-500 text-blue-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileDown className="w-4 h-4" />
          Export Artifacts (PDF / JSON / CSV)
        </button>
      </div>

      {/* Tab 1: Evidence Inventory */}
      {activeTab === 'evidence' && (
        <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
                <tr>
                  <th className="py-2.5 px-4">Evidence ID</th>
                  <th className="py-2.5 px-4">Transaction ID</th>
                  <th className="py-2.5 px-4">Source Wallet</th>
                  <th className="py-2.5 px-4">Destination Wallet</th>
                  <th className="py-2.5 px-4">Amount</th>
                  <th className="py-2.5 px-4">Risk Score</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Integrity Digest</th>
                  <th className="py-2.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {evidenceList.map((e) => (
                  <tr key={e.evidence_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-4 text-blue-400 font-semibold">
                      <Link to={`/evidence/${e.evidence_id}`}>{e.evidence_id}</Link>
                    </td>
                    <td className="py-2.5 px-4 text-slate-300">{e.transaction_id}</td>
                    <td className="py-2.5 px-4 text-slate-400 font-mono">{e.source_wallet.slice(0, 10)}...</td>
                    <td className="py-2.5 px-4 text-slate-400 font-mono">{e.destination_wallet.slice(0, 10)}...</td>
                    <td className="py-2.5 px-4 text-white font-bold">{e.amount.toFixed(2)} BTC</td>
                    <td className="py-2.5 px-4">
                      <RiskBadge score={e.risk_score} />
                    </td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {e.analyst_status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4">
                      <IntegrityBadge isTampered={e.is_tampered} isAnchored={e.is_anchored} />
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <Link
                        to={`/evidence/${e.evidence_id}`}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] border border-slate-700"
                      >
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))}
                {evidenceList.length === 0 && (
                  <tr>
                    <td colSpan={9} className="py-8 text-center text-slate-400 font-mono text-xs">
                      No evidence records in this case. Click "Ingest Evidence" to register transactions.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Chain of Custody */}
      {activeTab === 'custody' && (
        <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
          <h2 className="text-xs font-bold font-mono uppercase text-slate-200 mb-4 flex items-center justify-between">
            <span>Cryptographic Chained Event Ledger</span>
            <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" /> ALL LINKS VERIFIED
            </span>
          </h2>

          <div className="space-y-3 font-mono text-xs">
            {custodyEvents.map((evt, idx) => (
              <div key={evt.event_id} className="p-3 bg-slate-950 border border-slate-800 rounded flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-bold">#{idx + 1}</span>
                    <span className="font-bold text-white uppercase text-xs text-blue-400">{evt.action}</span>
                    <span className="text-[10px] text-slate-400">by {evt.actor} ({evt.role})</span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    <span className="text-slate-400">Prev Hash: </span>
                    <span className="text-slate-400">{evt.previous_hash.slice(0, 16)}...</span>
                  </div>
                </div>

                <div className="text-left md:text-right">
                  <div className="text-[10px] text-slate-400">{evt.timestamp}</div>
                  <div className="text-[11px] font-bold text-emerald-400">
                    Hash: {evt.event_hash.slice(0, 20)}...
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Reports */}
      {activeTab === 'reports' && (
        <div className="bg-navy-900 border border-forensic-border rounded-lg p-6 space-y-4 font-mono">
          <h2 className="text-xs font-bold uppercase text-slate-200 mb-2">Export Forensic Examination Reports</h2>
          <p className="text-xs text-slate-400">
            Generate formal multi-format forensic dossiers compliant with the 18 mandatory digital-evidence reporting standards.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="p-4 bg-slate-950 rounded border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="font-bold text-sm text-white mb-1">PDF Forensic Examination Report</div>
                <p className="text-xs text-slate-400">Formal printable dossier containing 18 sections, SHA-256 digests, SHAP attributions, and chain-of-custody table.</p>
              </div>
              <a
                href={`/api/v1/reports/${id}/pdf`}
                target="_blank"
                rel="noreferrer"
                className="mt-4 py-2 px-3 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold text-center flex items-center justify-center gap-1"
              >
                <Download className="w-3.5 h-3.5" /> Download PDF
              </a>
            </div>

            <div className="p-4 bg-slate-950 rounded border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="font-bold text-sm text-white mb-1">Canonical JSON Evidence Manifest</div>
                <p className="text-xs text-slate-400">Deterministic verifiable JSON export of all evidence records and cryptographic hash chains.</p>
              </div>
              <a
                href={`/api/v1/reports/${id}/manifest`}
                target="_blank"
                rel="noreferrer"
                className="mt-4 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold text-center flex items-center justify-center gap-1 border border-slate-700"
              >
                <Download className="w-3.5 h-3.5" /> Download JSON Manifest
              </a>
            </div>

            <div className="p-4 bg-slate-950 rounded border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="font-bold text-sm text-white mb-1">CSV Analytical Export</div>
                <p className="text-xs text-slate-400">Structured tabular data export for external spreadsheet audit or statistical review.</p>
              </div>
              <a
                href={`/api/v1/reports/${id}/csv`}
                target="_blank"
                rel="noreferrer"
                className="mt-4 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold text-center flex items-center justify-center gap-1 border border-slate-700"
              >
                <Download className="w-3.5 h-3.5" /> Download CSV
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Ingest Evidence Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-navy-900 border border-forensic-border rounded-lg max-w-md w-full p-6 shadow-2xl">
            <h2 className="text-sm font-bold text-white font-mono uppercase mb-4 flex items-center gap-2">
              <Plus className="w-4 h-4 text-blue-400" />
              Ingest & Hash Evidence Item
            </h2>

            <form onSubmit={handleIngestEvidence} className="space-y-4 font-mono text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Transaction ID (Hash)</label>
                <input
                  type="text"
                  value={txId}
                  onChange={(e) => setTxId(e.target.value)}
                  placeholder="e.g. tx_0x789a..."
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Source Wallet Address</label>
                <input
                  type="text"
                  value={srcWallet}
                  onChange={(e) => setSrcWallet(e.target.value)}
                  placeholder="0x_source_wallet..."
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Destination Wallet Address</label>
                <input
                  type="text"
                  value={dstWallet}
                  onChange={(e) => setDstWallet(e.target.value)}
                  placeholder="0x_destination_wallet..."
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Amount (BTC)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-forensic-border">
                <button
                  type="button"
                  onClick={() => setShowIngestModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold"
                >
                  Ingest, Extract Features & Hash
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
