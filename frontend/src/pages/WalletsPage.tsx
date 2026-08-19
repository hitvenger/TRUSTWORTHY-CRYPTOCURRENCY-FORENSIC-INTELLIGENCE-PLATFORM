import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Link } from 'react-router-dom';
import { Wallet, Search, ArrowRight, ShieldCheck, Activity } from 'lucide-react';
import { RiskBadge } from '../components/RiskBadge';

export const WalletsPage: React.FC = () => {
  const [walletList, setWalletList] = useState<any[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchWallets();
  }, []);

  const fetchWallets = async () => {
    try {
      setLoading(true);
      const res = await api.get('/graph/explore?limit=100');
      if (res.data?.nodes) {
        setWalletList(res.data.nodes);
      }
    } catch (err) {
      console.error('Failed to load wallets', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = walletList.filter((w) =>
    w.full_address.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Wallet className="w-5 h-5 text-blue-400" />
            WALLET INTELLIGENCE REPOSITORY
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Entity profiles, counterparty networks, and topological risk indicators.
          </p>
        </div>
      </div>

      <div className="flex gap-3 items-center bg-navy-900 border border-forensic-border p-3 rounded-lg">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by wallet address or cluster..."
          className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
        />
      </div>

      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
            <tr>
              <th className="py-2.5 px-4">Wallet Address</th>
              <th className="py-2.5 px-4">Inbound Txs</th>
              <th className="py-2.5 px-4">Outbound Txs</th>
              <th className="py-2.5 px-4">Total Volume</th>
              <th className="py-2.5 px-4">Max Risk Exposure</th>
              <th className="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filtered.map((w) => (
              <tr key={w.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-2.5 px-4 text-blue-400 font-bold">
                  <Link to={`/wallets/${w.full_address}`}>{w.full_address}</Link>
                </td>
                <td className="py-2.5 px-4 text-emerald-400 font-semibold">{w.in_txs}</td>
                <td className="py-2.5 px-4 text-blue-400 font-semibold">{w.out_txs}</td>
                <td className="py-2.5 px-4 text-white font-bold">{w.total_volume.toFixed(2)} BTC</td>
                <td className="py-2.5 px-4">
                  <RiskBadge score={w.max_risk} />
                </td>
                <td className="py-2.5 px-4 text-right">
                  <Link
                    to={`/wallets/${w.full_address}`}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] border border-slate-700 inline-flex items-center gap-1"
                  >
                    Profile <ArrowRight className="w-3 h-3" />
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
