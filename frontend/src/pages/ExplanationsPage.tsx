import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { EvidenceItem } from '../types';
import { RiskBadge } from '../components/RiskBadge';
import { Link } from 'react-router-dom';
import { HelpCircle, Search, Layers, Cpu, ArrowRight } from 'lucide-react';

export const ExplanationsPage: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<EvidenceItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchEvidence();
  }, []);

  const fetchEvidence = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dashboard/summary');
      if (res.data?.recent_leads) {
        setEvidenceList(res.data.recent_leads);
        if (res.data.recent_leads.length > 0) {
          setSelectedItem(res.data.recent_leads[0]);
        }
      }
    } catch (err) {
      console.error('Failed to load explanations', err);
    } finally {
      setLoading(false);
    }
  };

  const expl = selectedItem?.explanation_json || {};

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="border-b border-forensic-border pb-4">
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-purple-400" />
          SHAP FORENSIC EXPLAINABILITY EXPLORER
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-sans">
          Case-by-case feature attributions binding model decisions directly to canonical evidence records.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Evidence List Selector */}
        <div className="bg-navy-900 border border-forensic-border rounded-lg p-4 space-y-3">
          <h2 className="text-xs font-bold uppercase text-slate-200">Select Flagged Transaction</h2>
          <div className="space-y-2 max-h-[580px] overflow-y-auto">
            {evidenceList.map((item) => (
              <div
                key={item.evidence_id}
                onClick={() => setSelectedItem(item)}
                className={`p-3 rounded border cursor-pointer transition-colors ${
                  selectedItem?.evidence_id === item.evidence_id
                    ? 'bg-purple-950/40 border-purple-800 text-white'
                    : 'bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-900'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="font-bold text-blue-400">{item.transaction_id}</span>
                  <RiskBadge score={item.risk_score} />
                </div>
                <div className="text-[10px] text-slate-400 truncate">
                  {item.evidence_id} &bull; {item.amount?.toFixed(2)} BTC
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Deep Explanation Breakdown */}
        <div className="lg:col-span-2 space-y-6">
          {selectedItem ? (
            <>
              <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h2 className="text-xs font-bold uppercase text-slate-200">
                      Forensic Rationale: {selectedItem.transaction_id}
                    </h2>
                    <div className="text-[10px] text-slate-400">
                      Model Lineage: {selectedItem.model_id} (v{selectedItem.model_version})
                    </div>
                  </div>
                  <RiskBadge score={selectedItem.risk_score} />
                </div>

                <div className="p-3 bg-slate-950 border border-slate-800 rounded mb-4 font-sans text-xs text-slate-300">
                  <span className="text-purple-400 font-bold font-mono">AUTOMATED FORENSIC SUMMARY: </span>
                  {expl.plain_text_rationale || 'Flagged due to multi-signal topological risk and elevated transaction velocity.'}
                </div>

                <h3 className="text-[11px] font-bold text-slate-300 uppercase mb-2">Positive Risk Drivers (+ Impact)</h3>
                <div className="space-y-2 mb-4">
                  {expl.top_positive_contributors?.map((d: any, idx: number) => (
                    <div key={idx} className="p-2.5 bg-slate-950 rounded border border-slate-800 flex justify-between items-center">
                      <div>
                        <span className="text-red-400 font-bold mr-2">+{(d.shap_value || 0).toFixed(4)}</span>
                        <span className="text-slate-200 font-semibold">{d.display_name}</span>
                        <span className="text-slate-400 ml-2 text-[10px]">(Observed Value: {d.feature_value})</span>
                      </div>
                      <span className="text-[10px] text-red-400 uppercase font-bold">INCREASES RISK</span>
                    </div>
                  ))}
                </div>

                <h3 className="text-[11px] font-bold text-slate-300 uppercase mb-2">Negative Risk Drivers (&minus; Impact)</h3>
                <div className="space-y-2">
                  {expl.top_negative_contributors?.map((d: any, idx: number) => (
                    <div key={idx} className="p-2.5 bg-slate-950 rounded border border-slate-800 flex justify-between items-center">
                      <div>
                        <span className="text-emerald-400 font-bold mr-2">{(d.shap_value || 0).toFixed(4)}</span>
                        <span className="text-slate-200 font-semibold">{d.display_name}</span>
                        <span className="text-slate-400 ml-2 text-[10px]">(Observed Value: {d.feature_value})</span>
                      </div>
                      <span className="text-[10px] text-emerald-400 uppercase font-bold">REDUCES RISK</span>
                    </div>
                  ))}
                  {(!expl.top_negative_contributors || expl.top_negative_contributors.length === 0) && (
                    <div className="text-[10px] text-slate-400">No mitigating negative features observed.</div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-navy-900 border border-forensic-border rounded-lg p-12 text-center text-slate-400">
              Select a transaction on the left to inspect its SHAP decision drivers.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
