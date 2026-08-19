import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { EvidenceItem } from '../types';
import { IntegrityBadge, RiskBadge } from '../components/RiskBadge';
import { Link } from 'react-router-dom';
import { ShieldAlert, ShieldCheck, RefreshCw, AlertTriangle, ArrowRight } from 'lucide-react';

export const IntegrityPage: React.FC = () => {
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [verifyingAll, setVerifyingAll] = useState<boolean>(false);

  useEffect(() => {
    fetchEvidence();
  }, []);

  const fetchEvidence = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dashboard/summary');
      if (res.data?.recent_leads) {
        setEvidenceList(res.data.recent_leads);
      }
    } catch (err) {
      console.error('Failed to load evidence', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyAll = async () => {
    try {
      setVerifyingAll(true);
      for (const item of evidenceList) {
        await api.post(`/evidence/${item.evidence_id}/verify`);
      }
      await fetchEvidence();
    } catch (err) {
      console.error('Error verifying all evidence', err);
    } finally {
      setVerifyingAll(false);
    }
  };

  const tamperedCount = evidenceList.filter((e) => e.is_tampered).length;

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            EVIDENCE INTEGRITY & REAL-TIME TAMPER AUDIT
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Continuous cryptographic verification of canonical SHA-256 evidence digests against recorded registry values.
          </p>
        </div>

        <button
          onClick={handleVerifyAll}
          disabled={verifyingAll}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold flex items-center gap-2 shadow-sm shadow-blue-950"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${verifyingAll ? 'animate-spin' : ''}`} />
          Re-Audit All Evidence Digests
        </button>
      </div>

      {/* Tamper Alert Banner */}
      {tamperedCount > 0 ? (
        <div className="p-4 bg-red-950/60 border border-red-800 rounded-lg flex items-center gap-3 text-red-300">
          <AlertTriangle className="w-6 h-6 text-red-400 shrink-0" />
          <div>
            <div className="font-bold text-sm">SECURITY ALERT: {tamperedCount} TAMPERED EVIDENCE ITEM(S) DETECTED!</div>
            <div className="text-xs opacity-90 font-sans">
              Cryptographic SHA-256 hash divergence identified. The altered records failed mathematical verification and have been flagged.
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 bg-emerald-950/40 border border-emerald-800/80 rounded-lg flex items-center gap-3 text-emerald-300">
          <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
          <div>
            <div className="font-bold text-sm">ALL REPOSITORIES CRYPTOGRAPHICALLY VERIFIED</div>
            <div className="text-xs opacity-90 font-sans">
              Zero hash collisions or unauthorized byte mutations detected across active evidence manifests.
            </div>
          </div>
        </div>
      )}

      {/* Integrity Table */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
            <tr>
              <th className="py-2.5 px-4">Evidence ID</th>
              <th className="py-2.5 px-4">Transaction ID</th>
              <th className="py-2.5 px-4">Expected SHA-256 Digest</th>
              <th className="py-2.5 px-4">Integrity Status</th>
              <th className="py-2.5 px-4">Blockchain Anchor</th>
              <th className="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {evidenceList.map((e) => (
              <tr key={e.evidence_id} className={`hover:bg-slate-800/40 ${e.is_tampered ? 'bg-red-950/20' : ''}`}>
                <td className="py-2.5 px-4 text-blue-400 font-bold">
                  <Link to={`/evidence/${e.evidence_id}`}>{e.evidence_id}</Link>
                </td>
                <td className="py-2.5 px-4 text-slate-300">{e.transaction_id}</td>
                <td className="py-2.5 px-4 text-slate-400 break-all">{e.integrity_digest.slice(0, 32)}...</td>
                <td className="py-2.5 px-4">
                  <IntegrityBadge isTampered={e.is_tampered} isAnchored={e.is_anchored} />
                </td>
                <td className="py-2.5 px-4">
                  {e.is_anchored ? (
                    <span className="text-[10px] text-blue-400 bg-blue-950 px-1.5 py-0.5 rounded border border-blue-900">
                      Block #{e.blockchain_block}
                    </span>
                  ) : (
                    <span className="text-[10px] text-slate-400">Off-Chain</span>
                  )}
                </td>
                <td className="py-2.5 px-4 text-right">
                  <Link
                    to={`/evidence/${e.evidence_id}`}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] border border-slate-700 inline-flex items-center gap-1"
                  >
                    Inspect <ArrowRight className="w-3 h-3" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
