import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { History, ShieldCheck, RefreshCw } from 'lucide-react';

export const AuditPage: React.FC = () => {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchAuditEvents();
  }, []);

  const fetchAuditEvents = async () => {
    try {
      setLoading(true);
      const res = await api.get('/audit/all-events');
      setEvents(res.data || []);
    } catch (err) {
      console.error('Failed to load audit events', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <History className="w-5 h-5 text-blue-400" />
            SECURITY & FORENSIC AUDIT TRAIL
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Immutable sequential record of administrative access, verification runs, and role-based actions.
          </p>
        </div>

        <button
          onClick={fetchAuditEvents}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="bg-navy-900 border border-forensic-border rounded-lg overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-forensic-border">
            <tr>
              <th className="py-2.5 px-4">Event ID</th>
              <th className="py-2.5 px-4">Case ID</th>
              <th className="py-2.5 px-4">Actor (Role)</th>
              <th className="py-2.5 px-4">Forensic Action</th>
              <th className="py-2.5 px-4">Timestamp</th>
              <th className="py-2.5 px-4">Cryptographic Event Hash</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {events.map((e) => (
              <tr key={e.event_id} className="hover:bg-slate-800/40">
                <td className="py-2.5 px-4 text-blue-400 font-bold">{e.event_id}</td>
                <td className="py-2.5 px-4 text-slate-300">{e.case_id}</td>
                <td className="py-2.5 px-4 text-slate-200">{e.actor} <span className="text-slate-400 text-[10px]">({e.role})</span></td>
                <td className="py-2.5 px-4">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-950 text-blue-400 border border-blue-900 uppercase">
                    {e.action}
                  </span>
                </td>
                <td className="py-2.5 px-4 text-slate-400">{e.timestamp}</td>
                <td className="py-2.5 px-4 text-emerald-400 font-bold break-all">{e.event_hash.slice(0, 24)}...</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
