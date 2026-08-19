import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/client';
import { EvidenceItem } from '../types';
import { RiskBadge, IntegrityBadge, CorroborationBadge } from '../components/RiskBadge';
import { ArrowLeft, ArrowRightLeft, Cpu, HelpCircle, Layers, ShieldCheck, Activity } from 'lucide-react';

export const TransactionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [txData, setTxData] = useState<EvidenceItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (id) {
      fetchTransaction();
    }
  }, [id]);

  const fetchTransaction = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/transactions/${id}`);
      setTxData(res.data);
    } catch (err) {
      console.error('Failed to load transaction detail', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono text-xs">
        LOADING TRANSACTION INTELLIGENCE...
      </div>
    );
  }

  if (!txData) {
    return (
      <div className="p-8 text-center text-red-400 font-mono">
        Transaction not found in forensic database.
      </div>
    );
  }

  const expl = txData.explanation_json || {};
  const feats = txData.features_json || {};

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex items-center gap-2 text-slate-400">
        <Link to="/transactions" className="hover:text-white flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Transactions
        </Link>
        <span>/</span>
        <span className="text-slate-200">{txData.transaction_id}</span>
      </div>

      <div className="bg-navy-900 border border-forensic-border rounded-lg p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-blue-400 font-bold">{txData.transaction_id}</span>
            <RiskBadge score={txData.risk_score} />
            <IntegrityBadge isTampered={txData.is_tampered} isAnchored={txData.is_anchored} />
          </div>
          <h1 className="text-lg font-bold text-white">Cryptocurrency Transaction Investigation Dossier</h1>
        </div>

        <Link
          to={`/evidence/${txData.evidence_id}`}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center gap-1.5"
        >
          <Layers className="w-3.5 h-3.5" /> Open Canonical Evidence Record
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Core Attributes */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-3">Transaction Flow & Flow Metrics</h2>
            <div className="grid grid-cols-2 gap-3 bg-slate-950 p-3 rounded border border-slate-800">
              <div>
                <span className="text-slate-400 block text-[10px]">SOURCE WALLET</span>
                <Link to={`/wallets/${txData.source_wallet}`} className="text-blue-400 hover:underline break-all">
                  {txData.source_wallet}
                </Link>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">DESTINATION WALLET</span>
                <Link to={`/wallets/${txData.destination_wallet}`} className="text-blue-400 hover:underline break-all">
                  {txData.destination_wallet}
                </Link>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">AMOUNT</span>
                <span className="text-white font-bold text-sm">{txData.amount?.toFixed(4)} BTC</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">TIMESTAMP</span>
                <span className="text-slate-300">{txData.event_timestamp}</span>
              </div>
            </div>
          </div>

          {/* Extracted Temporal Graph Features */}
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-3">Extracted Historical Graph State G(t-)</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {Object.entries(feats).map(([k, v]) => (
                <div key={k} className="p-2 bg-slate-950 rounded border border-slate-800">
                  <span className="text-slate-400 text-[10px] block truncate">{k}</span>
                  <span className="text-slate-200 font-bold">{typeof v === 'number' ? v.toFixed(3) : String(v)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* SHAP & Multi-model scores */}
        <div className="space-y-6">
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5 space-y-3">
            <h2 className="text-xs font-bold uppercase text-slate-200">Forensic Decision Breakdown</h2>
            <div className="p-3 bg-slate-950 rounded border border-slate-800 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Random Forest Risk:</span>
                <span className="text-orange-400 font-bold">{txData.risk_score?.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Isolation Forest Anomaly:</span>
                <span className="text-purple-400 font-bold">{txData.anomaly_score?.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Uncertainty Bounds:</span>
                <span className="text-slate-200 font-bold">&plusmn;{txData.uncertainty_delta?.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Model Confidence:</span>
                <span className="text-emerald-400 font-bold">{txData.confidence}</span>
              </div>
            </div>
          </div>

          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-3">Top SHAP Positive Drivers</h2>
            <div className="space-y-2">
              {expl.top_positive_contributors?.map((d: any, i: number) => (
                <div key={i} className="p-2 bg-slate-950 rounded border border-slate-800">
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-200 font-semibold">{d.display_name}</span>
                    <span className="text-red-400 font-bold">+{(d.shap_value || 0).toFixed(4)}</span>
                  </div>
                  <div className="text-[10px] text-slate-400">Value: {d.feature_value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
