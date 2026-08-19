import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { EvidenceItem } from '../types';
import { RiskBadge, IntegrityBadge } from '../components/RiskBadge';
import { Link } from 'react-router-dom';
import { ArrowRightLeft, Search, Filter, Cpu, ArrowRight } from 'lucide-react';

export const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const res = await api.get('/dashboard/summary');
      if (res.data?.recent_leads) {
        setTransactions(res.data.recent_leads);
      }
    } catch (err) {
      console.error('Failed to load transactions', err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = transactions.filter((t) =>
    t.transaction_id.toLowerCase().includes(search.toLowerCase()) ||
    t.source_wallet.toLowerCase().includes(search.toLowerCase()) ||
    t.destination_wallet.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5 text-blue-400" />
            TRANSACTION TRIAGE & ANALYTICS
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Multi-model risk scoring, anomaly percentiles, and dynamic topological features across transaction streams.
          </p>
        </div>
      </div>

      <div className="flex gap-3 items-center bg-navy-900 border border-forensic-border p-3 rounded-lg">
        <Search className="w-4 h-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by Transaction ID, Source Wallet, or Destination Wallet..."
          className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
        />
      </div>

      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
            <tr>
              <th className="py-2.5 px-4">Transaction ID</th>
              <th className="py-2.5 px-4">Source Wallet</th>
              <th className="py-2.5 px-4">Destination Wallet</th>
              <th className="py-2.5 px-4">Amount</th>
              <th className="py-2.5 px-4">RF Risk</th>
              <th className="py-2.5 px-4">Anomaly Score</th>
              <th className="py-2.5 px-4">Confidence</th>
              <th className="py-2.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filtered.map((tx) => (
              <tr key={tx.evidence_id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-2.5 px-4 text-blue-400 font-bold">
                  <Link to={`/transactions/${tx.transaction_id}`}>{tx.transaction_id}</Link>
                </td>
                <td className="py-2.5 px-4 text-slate-400">{tx.source_wallet.slice(0, 12)}...</td>
                <td className="py-2.5 px-4 text-slate-400">{tx.destination_wallet.slice(0, 12)}...</td>
                <td className="py-2.5 px-4 text-white font-bold">{tx.amount.toFixed(2)} BTC</td>
                <td className="py-2.5 px-4">
                  <RiskBadge score={tx.risk_score} />
                </td>
                <td className="py-2.5 px-4 text-purple-400 font-bold">{tx.anomaly_score.toFixed(4)}</td>
                <td className="py-2.5 px-4 text-slate-400">&plusmn;{tx.uncertainty_delta?.toFixed(2)} ({tx.confidence})</td>
                <td className="py-2.5 px-4 text-right">
                  <Link
                    to={`/transactions/${tx.transaction_id}`}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] border border-slate-700 inline-flex items-center gap-1"
                  >
                    Triage <ArrowRight className="w-3 h-3" />
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
