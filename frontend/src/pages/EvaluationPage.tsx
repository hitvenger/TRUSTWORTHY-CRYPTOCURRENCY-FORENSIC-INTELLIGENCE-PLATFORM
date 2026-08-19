import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { FileBarChart, RefreshCw, Activity, Layers, CheckCircle } from 'lucide-react';

export const EvaluationPage: React.FC = () => {
  const [fiveSeeds, setFiveSeeds] = useState<any | null>(null);
  const [ablation, setAblation] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const fetchBenchmarks = async () => {
    try {
      setLoading(true);
      const [seedsRes, ablRes] = await Promise.all([
        api.get('/experiments/5seeds'),
        api.get('/experiments/ablation'),
      ]);
      setFiveSeeds(seedsRes.data);
      setAblation(ablRes.data);
    } catch (err) {
      console.error('Failed to load benchmarks', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center text-slate-400 font-mono text-xs">
        <Activity className="w-5 h-5 animate-spin mr-2 text-blue-400" />
        COMPUTING 5-SEED EMPIRICAL BENCHMARKS & ABLATION MATRIX...
      </div>
    );
  }

  const sMetrics = fiveSeeds?.metrics_summary;

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <FileBarChart className="w-5 h-5 text-blue-400" />
            EMPIRICAL EVALUATION & ABLATION STUDY
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Rigorous chronological 70/30 split benchmarks across 5 canonical paper seeds and 7 ablation configurations.
          </p>
        </div>

        <button
          onClick={fetchBenchmarks}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* 5-Seed Reproducibility Summary Table */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
        <h2 className="text-xs font-bold uppercase text-slate-200 mb-3 flex items-center justify-between">
          <span>5-Seed Benchmark (Seeds: 7, 19, 31, 43, 59 &bull; Chronological Split)</span>
          <span className="text-[10px] text-emerald-400">PAPER REPRODUCIBILITY PATH</span>
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-5">
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-400 block text-[10px]">PRECISION</span>
            <span className="text-emerald-400 font-bold text-sm">
              {sMetrics?.precision?.mean?.toFixed(4)} &plusmn; {sMetrics?.precision?.std?.toFixed(4)}
            </span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-400 block text-[10px]">RECALL</span>
            <span className="text-emerald-400 font-bold text-sm">
              {sMetrics?.recall?.mean?.toFixed(4)} &plusmn; {sMetrics?.recall?.std?.toFixed(4)}
            </span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-400 block text-[10px]">F1-SCORE</span>
            <span className="text-blue-400 font-bold text-sm">
              {sMetrics?.f1?.mean?.toFixed(4)} &plusmn; {sMetrics?.f1?.std?.toFixed(4)}
            </span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-400 block text-[10px]">ROC-AUC</span>
            <span className="text-purple-400 font-bold text-sm">
              {sMetrics?.roc_auc?.mean?.toFixed(4)} &plusmn; {sMetrics?.roc_auc?.std?.toFixed(4)}
            </span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-400 block text-[10px]">PR-AUC</span>
            <span className="text-purple-400 font-bold text-sm">
              {sMetrics?.pr_auc?.mean?.toFixed(4)} &plusmn; {sMetrics?.pr_auc?.std?.toFixed(4)}
            </span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-400 block text-[10px]">BRIER CALIBRATION</span>
            <span className="text-slate-200 font-bold text-sm">
              {sMetrics?.brier_score?.mean?.toFixed(4)} &plusmn; {sMetrics?.brier_score?.std?.toFixed(4)}
            </span>
          </div>
          <div className="p-3 bg-slate-950 rounded border border-slate-800">
            <span className="text-slate-400 block text-[10px]">LATENCY (PER TX)</span>
            <span className="text-slate-300 font-bold text-sm">
              {sMetrics?.latency_ms?.mean?.toFixed(3)} ms
            </span>
          </div>
        </div>

        {/* Individual Seed Runs Table */}
        <table className="w-full text-left bg-slate-950 rounded overflow-hidden border border-slate-800">
          <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] border-b border-slate-800">
            <tr>
              <th className="py-2 px-3">Evaluation Seed</th>
              <th className="py-2 px-3">Precision</th>
              <th className="py-2 px-3">Recall</th>
              <th className="py-2 px-3">F1-Score</th>
              <th className="py-2 px-3">ROC-AUC</th>
              <th className="py-2 px-3">PR-AUC</th>
              <th className="py-2 px-3">Brier Score</th>
              <th className="py-2 px-3">Latency (ms)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-850">
            {fiveSeeds?.individual_runs?.map((run: any) => (
              <tr key={run.seed} className="hover:bg-slate-900/50">
                <td className="py-2 px-3 text-blue-400 font-bold">Seed {run.seed}</td>
                <td className="py-2 px-3 text-slate-200">{run.precision.toFixed(4)}</td>
                <td className="py-2 px-3 text-slate-200">{run.recall.toFixed(4)}</td>
                <td className="py-2 px-3 text-emerald-400 font-bold">{run.f1.toFixed(4)}</td>
                <td className="py-2 px-3 text-purple-400 font-bold">{run.roc_auc.toFixed(4)}</td>
                <td className="py-2 px-3 text-purple-400">{run.pr_auc.toFixed(4)}</td>
                <td className="py-2 px-3 text-slate-300">{run.brier_score.toFixed(4)}</td>
                <td className="py-2 px-3 text-slate-400">{run.latency_per_sample_ms.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Formal 7-Configuration Ablation Study Matrix */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
        <h2 className="text-xs font-bold uppercase text-slate-200 mb-3 flex items-center justify-between">
          <span>7-Configuration Ablation Matrix</span>
          <span className="text-[10px] text-blue-400">FEATURE DYNAMICS ISOLATION</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left bg-slate-950 rounded overflow-hidden border border-slate-800">
            <thead className="bg-slate-900 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Configuration</th>
                <th className="py-2.5 px-4">Description</th>
                <th className="py-2.5 px-4">Precision</th>
                <th className="py-2.5 px-4">Recall</th>
                <th className="py-2.5 px-4">F1-Score</th>
                <th className="py-2.5 px-4">ROC-AUC</th>
                <th className="py-2.5 px-4">PR-AUC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {ablation?.ablation_summary?.map((row: any) => (
                <tr key={row.model_name} className="hover:bg-slate-900/50">
                  <td className="py-2.5 px-4 text-white font-bold">{row.model_name}</td>
                  <td className="py-2.5 px-4 text-slate-400 text-[11px] max-w-xs">{row.config_description}</td>
                  <td className="py-2.5 px-4 text-slate-200">{row.precision.toFixed(4)}</td>
                  <td className="py-2.5 px-4 text-slate-200">{row.recall.toFixed(4)}</td>
                  <td className="py-2.5 px-4 text-emerald-400 font-bold">{row.f1.toFixed(4)}</td>
                  <td className="py-2.5 px-4 text-purple-400 font-bold">{row.roc_auc.toFixed(4)}</td>
                  <td className="py-2.5 px-4 text-purple-400">{row.pr_auc.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
