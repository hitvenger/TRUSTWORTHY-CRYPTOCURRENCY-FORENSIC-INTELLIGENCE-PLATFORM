import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { GraphNode, GraphEdge } from '../types';
import { InvestigationGraphCanvas } from '../components/InvestigationGraphCanvas';
import { Network, Filter, RefreshCw, Activity, Layers } from 'lucide-react';

export const InvestigationGraphPage: React.FC = () => {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [minRisk, setMinRisk] = useState<number>(0.0);
  const [limit, setLimit] = useState<number>(150);

  useEffect(() => {
    fetchGraph();
  }, [minRisk, limit]);

  const fetchGraph = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/graph/explore?min_risk=${minRisk}&limit=${limit}`);
      setNodes(res.data.nodes || []);
      setEdges(res.data.edges || []);
    } catch (err) {
      console.error('Failed to load investigation graph', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-forensic-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Network className="w-5 h-5 text-blue-400" />
            INVESTIGATION GRAPH EXPLORER
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Interactive multi-hop cryptocurrency transaction graph with real-time risk coloring and topological clustering.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-navy-900 border border-forensic-border px-3 py-1.5 rounded">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-[10px] text-slate-400 uppercase">Min Risk:</span>
            <select
              value={minRisk}
              onChange={(e) => setMinRisk(parseFloat(e.target.value))}
              className="bg-transparent text-xs text-white focus:outline-none"
            >
              <option value="0.0" className="bg-slate-900">All (0.0+)</option>
              <option value="0.35" className="bg-slate-900">Medium+ (&ge; 0.35)</option>
              <option value="0.60" className="bg-slate-900">High+ (&ge; 0.60)</option>
              <option value="0.80" className="bg-slate-900">Critical (&ge; 0.80)</option>
            </select>
          </div>

          <button
            onClick={fetchGraph}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded flex items-center gap-1.5 border border-slate-700"
          >
            <RefreshCw className="w-3.5 h-3.5 text-blue-400" /> Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="h-[580px] bg-slate-950 border border-forensic-border rounded-lg flex items-center justify-center text-slate-400">
          <Activity className="w-5 h-5 animate-spin mr-2 text-blue-400" />
          CALCULATING GRAPH TOPOLOGY & DEGREE METRICS...
        </div>
      ) : (
        <InvestigationGraphCanvas nodes={nodes} edges={edges} />
      )}
    </div>
  );
};
