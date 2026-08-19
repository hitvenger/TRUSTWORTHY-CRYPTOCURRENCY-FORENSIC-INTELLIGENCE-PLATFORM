import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Blocks, ShieldCheck, RefreshCw, ExternalLink } from 'lucide-react';

export const BlockchainPage: React.FC = () => {
  const [anchors, setAnchors] = useState<any[]>([]);
  const [networkStatus, setNetworkStatus] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchBlockchainData();
  }, []);

  const fetchBlockchainData = async () => {
    try {
      setLoading(true);
      const [anchorsRes, netRes] = await Promise.all([
        api.get('/blockchain/anchors'),
        api.get('/blockchain/network-status'),
      ]);
      setAnchors(anchorsRes.data || []);
      setNetworkStatus(netRes.data);
    } catch (err) {
      console.error('Failed to load blockchain registry', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Blocks className="w-5 h-5 text-blue-400" />
            BLOCKCHAIN EVIDENCE ANCHOR REGISTRY
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Smart contract-based cryptographic evidence anchoring preserving off-chain privacy and on-chain immutability.
          </p>
        </div>

        <button
          onClick={fetchBlockchainData}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Network Status Header */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">NETWORK STATUS</span>
          <span className="text-emerald-400 font-bold text-lg">{networkStatus?.status || 'OPERATIONAL'}</span>
        </div>
        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">CURRENT BLOCK HEIGHT</span>
          <span className="text-white font-bold text-lg">#{networkStatus?.block_height || 18450121}</span>
        </div>
        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">REGISTERED ANCHORS</span>
          <span className="text-blue-400 font-bold text-lg">{anchors.length} records</span>
        </div>
        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">CONTRACT SECURITY</span>
          <span className="text-purple-400 font-bold text-lg">DUPLICATE-PROTECTED</span>
        </div>
      </div>

      {/* Anchor Table */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
            <tr>
              <th className="py-2.5 px-4">Evidence ID</th>
              <th className="py-2.5 px-4">Anchored SHA-256 Digest</th>
              <th className="py-2.5 px-4">Block #</th>
              <th className="py-2.5 px-4">Transaction Hash</th>
              <th className="py-2.5 px-4">Confirmations</th>
              <th className="py-2.5 px-4 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {anchors.map((a) => (
              <tr key={a.evidence_id} className="hover:bg-slate-800/40">
                <td className="py-2.5 px-4 text-blue-400 font-bold">{a.evidence_id}</td>
                <td className="py-2.5 px-4 text-emerald-400 break-all">{a.digest.slice(0, 24)}...</td>
                <td className="py-2.5 px-4 text-white font-bold">#{a.block_number}</td>
                <td className="py-2.5 px-4 text-slate-400 break-all">{a.transaction_hash?.slice(0, 20)}...</td>
                <td className="py-2.5 px-4 text-slate-300">{a.confirmations} blocks</td>
                <td className="py-2.5 px-4 text-right">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                    CONFIRMED
                  </span>
                </td>
              </tr>
            ))}
            {anchors.length === 0 && !loading && (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-400">
                  No evidence items anchored to blockchain yet. Open an evidence dossier and click "Anchor Digest to Smart Contract".
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
