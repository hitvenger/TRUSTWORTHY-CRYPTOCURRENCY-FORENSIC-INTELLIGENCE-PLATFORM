import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Case } from '../types';
import { FileText, Download, FileCheck, Layers, RefreshCw } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const res = await api.get('/cases');
      setCases(res.data || []);
      if (res.data?.length > 0) {
        setSelectedCaseId(res.data[0].case_id);
      }
    } catch (err) {
      console.error('Failed to load cases', err);
    } finally {
      setLoading(false);
    }
  };

  const selectedCase = cases.find((c) => c.case_id === selectedCaseId);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="border-b border-forensic-border pb-4">
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-400" />
          FORENSIC EXAMINATION REPORT GENERATOR
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-sans">
          Export court-ready PDF dossiers, canonical JSON evidence manifests, and CSV tables conforming to the 18 forensic criteria.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Case Selector */}
        <div className="bg-navy-900 border border-forensic-border rounded-lg p-5 space-y-3">
          <h2 className="text-xs font-bold uppercase text-slate-200">Select Target Case</h2>
          <div className="space-y-2 max-h-[500px] overflow-y-auto">
            {cases.map((c) => (
              <div
                key={c.case_id}
                onClick={() => setSelectedCaseId(c.case_id)}
                className={`p-3 rounded border cursor-pointer transition-colors ${
                  selectedCaseId === c.case_id
                    ? 'bg-blue-950/40 border-blue-600 text-white'
                    : 'bg-slate-950 border-slate-800 text-slate-300 hover:bg-slate-900'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="font-bold text-blue-400">{c.case_id}</span>
                  <span className="text-[10px] bg-slate-800 px-1.5 rounded">{c.status}</span>
                </div>
                <div className="text-xs font-semibold text-slate-200 truncate">{c.title}</div>
                <div className="text-[10px] text-slate-400 mt-1">{c.investigator}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Export Formats Console */}
        <div className="lg:col-span-2 space-y-6">
          {selectedCase ? (
            <div className="bg-navy-900 border border-forensic-border rounded-lg p-6 space-y-5">
              <div className="border-b border-forensic-border pb-4">
                <div className="text-xs text-blue-400 font-bold mb-1">{selectedCase.case_id}</div>
                <h2 className="text-base font-bold text-white">{selectedCase.title}</h2>
                <p className="text-slate-400 font-sans text-xs mt-1">{selectedCase.description || 'No description.'}</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-950 rounded border border-slate-800 flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-sm text-white mb-1">PDF Forensic Examination Report</h3>
                    <p className="text-slate-400 font-sans text-xs">Complete 18-section dossier with SHA-256 integrity digests and SHAP decision drivers.</p>
                  </div>
                  <a
                    href={`/api/v1/reports/${selectedCaseId}/pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-4 py-2 px-3 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold text-center flex items-center justify-center gap-1.5"
                  >
                    <Download className="w-3.5 h-3.5" /> Download PDF
                  </a>
                </div>

                <div className="p-4 bg-slate-950 rounded border border-slate-800 flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-sm text-white mb-1">Canonical JSON Evidence Manifest</h3>
                    <p className="text-slate-400 font-sans text-xs">Deterministic JSON schema export for automated external forensic verification.</p>
                  </div>
                  <a
                    href={`/api/v1/reports/${selectedCaseId}/manifest`}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-4 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-semibold text-center flex items-center justify-center gap-1.5 border border-slate-700"
                  >
                    <Download className="w-3.5 h-3.5" /> Download JSON
                  </a>
                </div>

                <div className="p-4 bg-slate-950 rounded border border-slate-800 flex flex-col justify-between">
                  <div>
                    <h3 className="font-bold text-sm text-white mb-1">CSV Analytical Export</h3>
                    <p className="text-slate-400 font-sans text-xs">Tabular feature and transaction export for spreadsheet analysis.</p>
                  </div>
                  <a
                    href={`/api/v1/reports/${selectedCaseId}/csv`}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-4 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-semibold text-center flex items-center justify-center gap-1.5 border border-slate-700"
                  >
                    <Download className="w-3.5 h-3.5" /> Download CSV
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-navy-900 border border-forensic-border rounded-lg p-12 text-center text-slate-400">
              Select a case to export examination dossiers.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
