import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/client';
import { RiskBadge } from '../components/RiskBadge';
import { ArrowLeft, Wallet, Network, ArrowRightLeft, ShieldCheck, Activity } from 'lucide-react';

export const WalletDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (id) {
      fetchWalletProfile();
    }
  }, [id]);

  const fetchWalletProfile = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/wallets/${id}`);
      setProfile(res.data);
    } catch (err) {
      console.error('Failed to load wallet profile', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono text-xs">
        LOADING WALLET DOSSIER...
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="p-8 text-center text-red-400 font-mono">
        Wallet address not found.
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex items-center gap-2 text-slate-400">
        <Link to="/wallets" className="hover:text-white flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Wallets
        </Link>
        <span>/</span>
        <span className="text-slate-200">{profile.address}</span>
      </div>

      <div className="bg-navy-900 border border-forensic-border rounded-lg p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-blue-400 font-bold">CRYPTO ENTITY PROFILE</span>
            <RiskBadge score={profile.max_risk_score} />
          </div>
          <h1 className="text-lg font-bold text-white break-all">{profile.address}</h1>
        </div>

        <Link
          to={`/investigation/graph`}
          className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold flex items-center gap-1.5"
        >
          <Network className="w-3.5 h-3.5" /> Locate in Graph
        </Link>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">TOTAL TRANSACTIONS</span>
          <span className="text-white font-bold text-xl">{profile.transaction_count}</span>
          <span className="text-[10px] text-slate-400 mt-1 block">In: {profile.inbound_count} | Out: {profile.outbound_count}</span>
        </div>

        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">TOTAL RECEIVED</span>
          <span className="text-emerald-400 font-bold text-xl">{profile.total_received?.toFixed(2)} BTC</span>
        </div>

        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">TOTAL SENT</span>
          <span className="text-blue-400 font-bold text-xl">{profile.total_sent?.toFixed(2)} BTC</span>
        </div>

        <div className="bg-navy-900 border border-forensic-border p-4 rounded-lg">
          <span className="text-slate-400 block text-[10px]">UNIQUE COUNTERPARTIES</span>
          <span className="text-purple-400 font-bold text-xl">{profile.unique_counterparty_count} entities</span>
        </div>
      </div>

      {/* Recent Associated Transactions */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <div className="p-4 border-b border-forensic-border bg-slate-950/40">
          <h2 className="text-xs font-bold uppercase text-slate-200">Associated Transactions ({profile.recent_transactions?.length || 0})</h2>
        </div>
        <table className="w-full text-left">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
            <tr>
              <th className="py-2 px-4">Tx ID</th>
              <th className="py-2 px-4">Direction</th>
              <th className="py-2 px-4">Counterparty</th>
              <th className="py-2 px-4">Amount</th>
              <th className="py-2 px-4">Risk</th>
              <th className="py-2 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {profile.recent_transactions?.map((tx: any) => (
              <tr key={tx.evidence_id} className="hover:bg-slate-800/40">
                <td className="py-2 px-4 text-blue-400 font-semibold">{tx.transaction_id}</td>
                <td className="py-2 px-4">
                  <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    tx.direction === 'INBOUND' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-blue-950 text-blue-400 border border-blue-800'
                  }`}>
                    {tx.direction}
                  </span>
                </td>
                <td className="py-2 px-4 text-slate-300">{tx.counterparty?.slice(0, 14)}...</td>
                <td className="py-2 px-4 text-white font-bold">{tx.amount?.toFixed(2)} BTC</td>
                <td className="py-2 px-4"><RiskBadge score={tx.risk_score} /></td>
                <td className="py-2 px-4 text-right">
                  <Link to={`/evidence/${tx.evidence_id}`} className="text-blue-400 hover:underline">
                    Inspect Evidence
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
