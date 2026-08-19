import React from 'react';

interface RiskBadgeProps {
  score?: number;
  level?: string;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ score, level, className = '' }) => {
  let displayLevel = level;
  if (!displayLevel && score !== undefined) {
    if (score >= 0.8) displayLevel = 'CRITICAL';
    else if (score >= 0.6) displayLevel = 'HIGH';
    else if (score >= 0.35) displayLevel = 'MEDIUM';
    else displayLevel = 'LOW';
  }

  const styles = {
    CRITICAL: 'bg-red-950/80 text-red-400 border-red-800/60 shadow-sm shadow-red-950',
    HIGH: 'bg-orange-950/80 text-orange-400 border-orange-800/60 shadow-sm shadow-orange-950',
    MEDIUM: 'bg-yellow-950/80 text-yellow-400 border-yellow-800/60',
    LOW: 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60',
  }[displayLevel || 'LOW'] || 'bg-slate-800 text-slate-300 border-slate-700';

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold border ${styles} ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${
        displayLevel === 'CRITICAL' ? 'bg-red-500 animate-pulse' :
        displayLevel === 'HIGH' ? 'bg-orange-500' :
        displayLevel === 'MEDIUM' ? 'bg-yellow-500' : 'bg-emerald-500'
      }`} />
      {displayLevel} {score !== undefined ? `(${score.toFixed(2)})` : ''}
    </span>
  );
};

export const IntegrityBadge: React.FC<{ isTampered: boolean; isAnchored?: boolean }> = ({ isTampered, isAnchored }) => {
  if (isTampered) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-rose-950 text-rose-300 border border-rose-700 animate-pulse">
        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        TAMPER DETECTED
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-mono font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
      INTEGRITY VERIFIED
      {isAnchored && <span className="ml-1 text-[10px] bg-blue-900/60 text-blue-300 px-1 rounded border border-blue-700">ON-CHAIN</span>}
    </span>
  );
};

export const CorroborationBadge: React.FC<{ status: string; count?: number }> = ({ status, count }) => {
  const styles = {
    STRONG: 'bg-purple-950/70 text-purple-300 border-purple-800',
    MODERATE: 'bg-blue-950/70 text-blue-300 border-blue-800',
    WEAK: 'bg-slate-800 text-slate-400 border-slate-700',
    NONE: 'bg-slate-900 text-slate-500 border-slate-800',
  }[status || 'NONE'] || 'bg-slate-800 text-slate-400 border-slate-700';

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-medium border ${styles}`}>
      CORROBORATION: {status} {count !== undefined ? `(${count})` : ''}
    </span>
  );
};
