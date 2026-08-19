import React, { useState } from 'react';
import api from '../api/client';
import { RiskBadge, CorroborationBadge } from '../components/RiskBadge';
import { Cpu, Play, HelpCircle, Layers, Activity, AlertTriangle } from 'lucide-react';

export const AIAnalysisPage: React.FC = () => {
  const [txId, setTxId] = useState<string>('tx_live_investigation_001');
  const [srcWallet, setSrcWallet] = useState<string>('0x_mixer_entry_001');
  const [dstWallet, setDstWallet] = useState<string>('0x_mixer_exit_002');
  const [amount, setAmount] = useState<string>('45.0');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const res = await api.post('/transactions/analyze', {
        transaction_id: txId,
        source_wallet: srcWallet,
        destination_wallet: dstWallet,
        amount: parseFloat(amount) || 10.0,
        timestamp: Date.now() / 1000,
      });
      setResult(res.data);
    } catch (err) {
      console.error('Failed to analyze transaction', err);
    } finally {
      setLoading(false);
    }
  };

  const riskProf = result?.risk_profile;
  const expl = result?.explanation;

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="border-b border-forensic-border pb-4">
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Cpu className="w-5 h-5 text-blue-400" />
          REAL-TIME AI FORENSIC RISK & ANOMALY SCORING CONSOLE
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-sans">
          Execute multi-model inference (Random Forest Baseline + Isolation Forest + SHAP Explainability) across arbitrary transactions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Parameters Form */}
        <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
          <h2 className="text-xs font-bold uppercase text-slate-200 mb-4">Transaction Parameters</h2>

          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label className="block text-slate-400 mb-1 text-[10px]">TRANSACTION IDENTIFIER</label>
              <input
                type="text"
                value={txId}
                onChange={(e) => setTxId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1 text-[10px]">SOURCE WALLET ADDRESS</label>
              <input
                type="text"
                value={srcWallet}
                onChange={(e) => setSrcWallet(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1 text-[10px]">DESTINATION WALLET ADDRESS</label>
              <input
                type="text"
                value={dstWallet}
                onChange={(e) => setDstWallet(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1 text-[10px]">AMOUNT (BTC)</label>
              <input
                type="number"
                step="0.0001"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold flex items-center justify-center gap-2 shadow-sm shadow-blue-950"
            >
              {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Run Analytical Scoring Pipeline
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <>
              <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h2 className="text-xs font-bold uppercase text-slate-200">Analytical Output Synthesis</h2>
                    <div className="text-[10px] text-slate-400">Target Tx: {result.transaction_id}</div>
                  </div>
                  <RiskBadge score={riskProf?.overall_risk} />
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-3 rounded border border-slate-800">
                  <div>
                    <span className="text-slate-400 block text-[10px]">FUSED RISK SCORE</span>
                    <span className="text-orange-400 font-bold text-sm">{riskProf?.overall_risk?.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">ANOMALY SCORE</span>
                    <span className="text-purple-400 font-bold text-sm">{riskProf?.subscores?.anomaly_score?.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">UNCERTAINTY</span>
                    <span className="text-slate-200 font-bold text-sm">&plusmn;{riskProf?.uncertainty?.uncertainty_delta?.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">CORROBORATION</span>
                    <span className="text-blue-400 font-bold text-sm">{riskProf?.corroboration?.status}</span>
                  </div>
                </div>

                <div className="mt-3 p-3 bg-slate-950 border border-slate-800 rounded text-slate-300 font-sans text-xs">
                  <span className="text-blue-400 font-bold font-mono">PRIORITY RECOMMENDATION: </span>
                  {riskProf?.priority_description}
                </div>
              </div>

              {/* SHAP Drivers */}
              <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
                <h2 className="text-xs font-bold uppercase text-slate-200 mb-3 flex items-center gap-1.5 text-purple-400">
                  <HelpCircle className="w-4 h-4" />
                  SHAP Decision Attributions (Top Contributors)
                </h2>
                <div className="space-y-2">
                  {expl?.top_positive_contributors?.map((d: any, idx: number) => (
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
              </div>
            </>
          ) : (
            <div className="bg-navy-900 border border-forensic-border rounded-lg p-12 text-center text-slate-400">
              Enter transaction parameters on the left and click "Run Analytical Scoring Pipeline" to inspect real-time risk scores and SHAP explanations.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
