import React, { useRef, useEffect, useState } from 'react';
import { GraphNode, GraphEdge } from '../types';
import { RiskBadge } from './RiskBadge';
import { ArrowUpRight, Search, ZoomIn, ZoomOut, RefreshCw, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface GraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onSelectNode?: (node: GraphNode) => void;
  onSelectEdge?: (edge: GraphEdge) => void;
}

export const InvestigationGraphCanvas: React.FC<GraphProps> = ({
  nodes,
  edges,
  onSelectNode,
  onSelectEdge,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const navigate = useNavigate();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Compute node positions deterministically on a circular/force layout
  const [nodePositions, setNodePositions] = useState<Record<string, { x: number; y: number }>>({});

  useEffect(() => {
    if (!nodes.length) return;
    const positions: Record<string, { x: number; y: number }> = {};
    const width = 800;
    const height = 550;
    const radius = Math.min(width, height) * 0.38;
    const centerX = width / 2;
    const centerY = height / 2;

    nodes.forEach((node, idx) => {
      // Clustered circular arrangement
      const angle = (idx / nodes.length) * 2 * Math.PI;
      // Add slight jitter for visual organic structure
      const dist = radius * (0.65 + 0.35 * (idx % 3));
      positions[node.id] = {
        x: centerX + Math.cos(angle) * dist,
        y: centerY + Math.sin(angle) * dist,
      };
    });
    setNodePositions(positions);
  }, [nodes]);

  // Draw Graph Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    // Apply pan and zoom
    ctx.translate(pan.x, pan.y);
    ctx.scale(zoom, zoom);

    // 1. Draw Edges
    edges.forEach((edge) => {
      const srcPos = nodePositions[edge.source];
      const dstPos = nodePositions[edge.target];
      if (!srcPos || !dstPos) return;

      const isSelected = selectedEdge?.id === edge.id;
      ctx.beginPath();
      ctx.moveTo(srcPos.x, srcPos.y);
      ctx.lineTo(dstPos.x, dstPos.y);

      // Edge styling based on risk and selection
      if (isSelected) {
        ctx.strokeStyle = '#60a5fa';
        ctx.lineWidth = 3.5;
      } else if (edge.risk_score >= 0.70) {
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
        ctx.lineWidth = Math.min(4, Math.max(1.5, edge.amount / 20));
      } else {
        ctx.strokeStyle = 'rgba(71, 85, 105, 0.4)';
        ctx.lineWidth = 1.2;
      }
      ctx.stroke();

      // Arrow head for directed transaction
      const headlen = 8;
      const dx = dstPos.x - srcPos.x;
      const dy = dstPos.y - srcPos.y;
      const angle = Math.atan2(dy, dx);
      const targetRadius = 18;
      const arrowX = dstPos.x - Math.cos(angle) * targetRadius;
      const arrowY = dstPos.y - Math.sin(angle) * targetRadius;

      ctx.beginPath();
      ctx.moveTo(arrowX, arrowY);
      ctx.lineTo(arrowX - headlen * Math.cos(angle - Math.PI / 6), arrowY - headlen * Math.sin(angle - Math.PI / 6));
      ctx.lineTo(arrowX - headlen * Math.cos(angle + Math.PI / 6), arrowY - headlen * Math.sin(angle + Math.PI / 6));
      ctx.fillStyle = ctx.strokeStyle;
      ctx.fill();
    });

    // 2. Draw Nodes
    nodes.forEach((node) => {
      const pos = nodePositions[node.id];
      if (!pos) return;

      const isSelected = selectedNode?.id === node.id;
      const radius = isSelected ? 20 : Math.max(12, Math.min(22, 10 + (node.in_txs + node.out_txs) * 1.5));

      // Node Circle
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius, 0, 2 * Math.PI);

      // Fill color
      ctx.fillStyle = '#0f172a';
      ctx.fill();

      // Stroke color based on risk
      if (isSelected) {
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 3.5;
      } else if (node.max_risk >= 0.8) {
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2.5;
      } else if (node.max_risk >= 0.6) {
        ctx.strokeStyle = '#f97316';
        ctx.lineWidth = 2.0;
      } else {
        ctx.strokeStyle = '#22c55e';
        ctx.lineWidth = 1.5;
      }
      ctx.stroke();

      // Node label
      ctx.fillStyle = '#e2e8f0';
      ctx.font = isSelected ? 'bold 10px JetBrains Mono' : '9px JetBrains Mono';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, pos.x, pos.y + radius + 12);
    });

    ctx.restore();
  }, [nodes, edges, nodePositions, zoom, pan, selectedNode, selectedEdge]);

  // Click detection on canvas
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = (e.clientX - rect.left - pan.x) / zoom;
    const clickY = (e.clientY - rect.top - pan.y) / zoom;

    // Check node click
    let clickedNode: GraphNode | null = null;
    for (const node of nodes) {
      const pos = nodePositions[node.id];
      if (!pos) continue;
      const dist = Math.hypot(clickX - pos.x, clickY - pos.y);
      if (dist <= 20) {
        clickedNode = node;
        break;
      }
    }

    if (clickedNode) {
      setSelectedNode(clickedNode);
      setSelectedEdge(null);
      if (onSelectNode) onSelectNode(clickedNode);
    } else {
      setSelectedNode(null);
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="relative border border-forensic-border rounded-lg bg-slate-950 overflow-hidden">
      {/* Controls Overlay */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 p-1.5 rounded-md backdrop-blur">
        <button
          onClick={() => setZoom((z) => Math.min(z + 0.2, 2.5))}
          className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z - 0.2, 0.4))}
          className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => { setZoom(1.0); setPan({ x: 0, y: 0 }); }}
          className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800"
          title="Reset View"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
        <div className="h-4 w-[1px] bg-slate-800 mx-1" />
        <span className="text-[11px] font-mono text-slate-400 px-1">
          {nodes.length} Nodes &bull; {edges.length} Edges
        </span>
      </div>

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        width={900}
        height={580}
        onClick={handleCanvasClick}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        className="w-full h-[580px] cursor-grab active:cursor-grabbing block"
      />

      {/* Selected Node Inspector Flyout */}
      {selectedNode && (
        <div className="absolute bottom-3 right-3 z-10 w-80 bg-slate-900/95 border border-forensic-border rounded-lg p-4 shadow-xl backdrop-blur">
          <div className="flex justify-between items-start mb-2">
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-400">Inspected Wallet Node</div>
              <div className="text-xs font-mono font-bold text-white break-all">{selectedNode.full_address}</div>
            </div>
            <RiskBadge score={selectedNode.max_risk} />
          </div>

          <div className="grid grid-cols-2 gap-2 my-3 text-xs bg-slate-950 p-2.5 rounded border border-slate-800 font-mono">
            <div>
              <span className="text-slate-400 block text-[10px]">INBOUND TXS</span>
              <span className="text-emerald-400 font-bold">{selectedNode.in_txs}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">OUTBOUND TXS</span>
              <span className="text-blue-400 font-bold">{selectedNode.out_txs}</span>
            </div>
            <div className="col-span-2">
              <span className="text-slate-400 block text-[10px]">TOTAL VOLUME</span>
              <span className="text-white font-bold">{selectedNode.total_volume.toFixed(2)} BTC</span>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => navigate(`/wallets/${selectedNode.full_address}`)}
              className="flex-1 py-1.5 px-3 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold flex items-center justify-center gap-1"
            >
              <Eye className="w-3.5 h-3.5" />
              Wallet Dossier
            </button>
            <button
              onClick={() => setSelectedNode(null)}
              className="py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
