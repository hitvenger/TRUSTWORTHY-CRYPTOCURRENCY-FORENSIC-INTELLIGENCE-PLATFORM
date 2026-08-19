import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Sliders, ShieldCheck, Activity, AlertTriangle, Layers } from 'lucide-react';

export const ModelsPage: React.FC = () => {
  const [models, setModels] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedModel, setSelectedModel] = useState<any | null>(null);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const res = await api.get('/models');
      setModels(res.data || []);
      if (res.data?.length > 0) {
        setSelectedModel(res.data[0]);
      }
    } catch (err) {
      console.error('Failed to load models', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="border-b border-forensic-border pb-4">
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Sliders className="w-5 h-5 text-blue-400" />
          MODEL CARDS, GOVERNANCE & DRIFT REGISTRY
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-sans">
          Formal model cards, training specifications, prohibited use boundaries, and Population Stability Index (PSI) drift telemetry.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model List */}
        <div className="space-y-3">
          {models.map((m) => (
            <div
              key={m.model_id}
              onClick={() => setSelectedModel(m)}
              className={`p-4 bg-navy-900 border rounded-lg cursor-pointer transition-colors ${
                selectedModel?.model_id === m.model_id
                  ? 'border-blue-500 bg-blue-950/20'
                  : 'border-forensic-border hover:border-slate-700'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-bold text-white text-xs">{m.name}</span>
                <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.5 rounded font-bold">
                  v{m.version}
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-sans">{m.model_type}</div>
              <div className="mt-2 text-[10px] text-emerald-400 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" /> Drift Status: {m.drift_status}
              </div>
            </div>
          ))}
        </div>

        {/* Selected Model Card Detailed Specs */}
        <div className="lg:col-span-2 space-y-6">
          {selectedModel && (
            <div className="bg-navy-900 border border-forensic-border rounded-lg p-6 space-y-5">
              <div className="flex justify-between items-start border-b border-forensic-border pb-4">
                <div>
                  <h2 className="text-base font-bold text-white">{selectedModel.name}</h2>
                  <div className="text-slate-400 text-xs mt-0.5">Model ID: {selectedModel.model_id}</div>
                </div>
                <span className="px-2.5 py-1 bg-blue-950 text-blue-300 border border-blue-800 rounded font-bold">
                  {selectedModel.model_type}
                </span>
              </div>

              <div>
                <h3 className="text-slate-400 uppercase text-[10px] font-bold mb-1">Intended Forensic Use</h3>
                <p className="text-slate-200 font-sans text-xs">{selectedModel.intended_use}</p>
              </div>

              <div>
                <h3 className="text-rose-400 uppercase text-[10px] font-bold mb-1">Prohibited Use & Forensic Boundary</h3>
                <p className="text-slate-300 font-sans text-xs">{selectedModel.prohibited_use}</p>
              </div>

              <div>
                <h3 className="text-slate-400 uppercase text-[10px] font-bold mb-1">Hyperparameter Configuration</h3>
                <pre className="bg-slate-950 p-3 rounded border border-slate-800 text-[11px] text-blue-300 overflow-x-auto">
                  {JSON.stringify(selectedModel.hyperparameters, null, 2)}
                </pre>
              </div>

              {selectedModel.performance_metrics && (
                <div>
                  <h3 className="text-slate-400 uppercase text-[10px] font-bold mb-2">Empirical Benchmark Metrics</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-3 rounded border border-slate-800">
                    <div>
                      <span className="text-slate-400 block text-[10px]">F1-SCORE</span>
                      <span className="text-emerald-400 font-bold text-sm">{selectedModel.performance_metrics.f1_score}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">ROC-AUC</span>
                      <span className="text-blue-400 font-bold text-sm">{selectedModel.performance_metrics.roc_auc}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">PR-AUC</span>
                      <span className="text-purple-400 font-bold text-sm">{selectedModel.performance_metrics.pr_auc}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">INFERENCE LATENCY</span>
                      <span className="text-white font-bold text-sm">{selectedModel.performance_metrics.latency_ms} ms</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
