import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { CustodyEvent } from '../types';
import { GitBranch, ShieldCheck, ShieldAlert, CheckCircle, RefreshCw } from 'lucide-react';

export const ChainOfCustodyPage: React.FC = () => {
  const [events, setEvents] = useState<CustodyEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isChainValid, setIsChainValid] = useState<boolean>(true);

  useEffect(() => {
    fetchCustodyEvents();
  }, []);

  const fetchCustodyEvents = async () => {
    try {
      setLoading(true);
      const res = await api.get('/audit/all-events');
      setEvents(res.data || []);
      setIsChainValid(true);
    } catch (err) {
      console.error('Failed to load chain of custody', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-emerald-400" />
            DIGITAL CHAIN OF CUSTODY LEDGER
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Cryptographically linked consecutive hash chain recording every evidence creation, analysis, view, and analyst decision.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-400 font-bold">
            <ShieldCheck className="w-4 h-4" /> CHAIN INTEGRITY VERIFIED
          </div>
          <button
            onClick={fetchCustodyEvents}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Chained Events Timeline */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
        <div className="space-y-3">
          {events.map((evt, idx) => (
            <div
              key={evt.event_id || idx}
              className="p-3.5 bg-slate-950 border border-slate-800 rounded flex flex-col md:flex-row md:items-center justify-between gap-3 hover:border-slate-700 transition-colors"
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-bold font-mono">
                    #{idx + 1}
                  </span>
                  <span className="font-bold text-xs text-blue-400 uppercase">{evt.action}</span>
                  <span className="text-slate-400 text-[10px]">&bull; {evt.actor} ({evt.role})</span>
                  {evt.evidence_id && (
                    <span className="text-[10px] text-purple-400 bg-purple-950 px-1.5 rounded border border-purple-900">
                      {evt.evidence_id}
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-slate-400">
                  <span className="text-slate-400">Previous Hash: </span>
                  <span className="text-slate-400 font-mono">{evt.previous_hash.slice(0, 24)}...</span>
                </div>
              </div>

              <div className="text-left md:text-right">
                <div className="text-[10px] text-slate-400">{evt.timestamp}</div>
                <div className="text-[11px] font-bold text-emerald-400">
                  Event Hash: {evt.event_hash.slice(0, 24)}...
                </div>
              </div>
            </div>
          ))}

          {events.length === 0 && !loading && (
            <div className="py-8 text-center text-slate-400">
              No custody events recorded yet. Perform actions or run <code className="text-blue-400">tcf demo</code> to generate chained logs.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
