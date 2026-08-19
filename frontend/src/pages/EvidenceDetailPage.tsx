import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/client';
import { EvidenceItem } from '../types';
import { RiskBadge, IntegrityBadge, CorroborationBadge } from '../components/RiskBadge';
import {
  FileCheck,
  ShieldCheck,
  ShieldAlert,
  ArrowLeft,
  Blocks,
  Cpu,
  UserCheck,
  RotateCcw,
  AlertTriangle,
  Copy,
  Check,
  Layers,
  HelpCircle
} from 'lucide-react';

export const EvidenceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [evidence, setEvidence] = useState<EvidenceItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [verificationStatus, setVerificationStatus] = useState<any>(null);
  const [copied, setCopied] = useState<boolean>(false);

  // Tamper simulation state
  const [tamperAmount, setTamperAmount] = useState<string>('999999.0');
  const [isTamperingLoading, setIsTamperingLoading] = useState<boolean>(false);

  // Analyst review state
  const [reviewState, setReviewState] = useState<string>('FORENSIC_FINDING');
  const [reviewSummary, setReviewSummary] = useState<string>('Confirmed illicit peeling chain transfer with high velocity burst.');
  const [reviewRationale, setReviewRationale] = useState<string>('Topological graph features and SHAP drivers confirm anomalous fund dispersal.');

  useEffect(() => {
    if (id) {
      fetchEvidence();
    }
  }, [id]);

  const fetchEvidence = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/evidence/${id}`);
      setEvidence(res.data);
      // Run initial integrity check
      const vRes = await api.post(`/evidence/${id}/verify`);
      setVerificationStatus(vRes.data);
    } catch (err) {
      console.error('Failed to load evidence details', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    try {
      const vRes = await api.post(`/evidence/${id}/verify`);
      setVerificationStatus(vRes.data);
    } catch (err) {
      console.error('Verification failed', err);
    }
  };

  const handleSimulateTamper = async () => {
    try {
      setIsTamperingLoading(true);
      await api.post(`/evidence/${id}/tamper`, {
        field_to_modify: 'amount',
        new_value: parseFloat(tamperAmount) || 999999.0,
      });
      await fetchEvidence();
    } catch (err) {
      console.error('Failed to simulate tamper', err);
    } finally {
      setIsTamperingLoading(false);
    }
  };

  const handleRestoreEvidence = async () => {
    try {
      setIsTamperingLoading(true);
      await api.post(`/evidence/${id}/restore`, {
        field_to_modify: 'amount',
        new_value: evidence?.explanation_json?.top_positive_contributors ? 25.5 : 10.0,
      });
      await fetchEvidence();
    } catch (err) {
      console.error('Failed to restore evidence', err);
    } finally {
      setIsTamperingLoading(false);
    }
  };

  const handleAnchorToBlockchain = async () => {
    try {
      await api.post(`/evidence/${id}/anchor`, {
        evidence_id: id,
        submitter: '0x71C8A3dE5531b988fE7aE',
      });
      fetchEvidence();
    } catch (err) {
      console.error('Failed to anchor evidence', err);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!evidence) return;
    try {
      await api.post('/analyst-review', {
        case_id: evidence.case_id,
        evidence_id: evidence.evidence_id,
        new_state: reviewState,
        finding_summary: reviewSummary,
        rationale: reviewRationale,
        corroborating_notes: 'Corroborated by independent Isolation Forest anomaly score and topological clustering.',
      });
      fetchEvidence();
    } catch (err) {
      console.error('Failed to submit analyst review', err);
    }
  };

  const copyCanonicalJson = () => {
    if (!evidence) return;
    const canonicalPayload = {
      evidence_id: evidence.evidence_id,
      case_id: evidence.case_id,
      transaction_id: evidence.transaction_id,
      source_wallet: evidence.source_wallet,
      destination_wallet: evidence.destination_wallet,
      amount: evidence.amount,
      model_id: evidence.model_id,
      model_version: evidence.model_version,
      risk_score: evidence.risk_score,
      anomaly_score: evidence.anomaly_score,
      integrity_digest: evidence.integrity_digest,
    };
    navigator.clipboard.writeText(JSON.stringify(canonicalPayload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono text-xs">
        LOADING FORENSIC EVIDENCE DOSSIER...
      </div>
    );
  }

  if (!evidence) {
    return (
      <div className="p-8 text-center text-red-400 font-mono">
        Evidence item not found.
      </div>
    );
  }

  const expl = evidence.explanation_json || {};
  const corrob = evidence.corroboration_json || {};

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto font-mono text-xs">
      {/* Breadcrumbs */}
      <div className="flex items-center gap-2 text-slate-400">
        <Link to="/evidence" className="hover:text-white flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" /> Evidence
        </Link>
        <span>/</span>
        <span className="text-slate-200 font-bold">{evidence.evidence_id}</span>
      </div>

      {/* Header Banner */}
      <div className="bg-navy-900 border border-forensic-border rounded-lg p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm font-bold text-blue-400">{evidence.evidence_id}</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
              STATUS: {evidence.analyst_status}
            </span>
            <RiskBadge score={evidence.risk_score} />
          </div>
          <h1 className="text-lg font-bold text-white tracking-tight">
            Transaction Evidence: {evidence.transaction_id}
          </h1>
          <div className="text-[11px] text-slate-400 mt-1">
            Acquired from {evidence.source} &bull; Case: <Link to={`/cases/${evidence.case_id}`} className="text-blue-400 hover:underline">{evidence.case_id}</Link>
          </div>
        </div>

        {/* Verification Status Badge */}
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-lg border flex items-center gap-3 ${
            verificationStatus?.is_valid
              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-400'
              : 'bg-red-950/40 border-red-800 text-red-400 animate-pulse'
          }`}>
            {verificationStatus?.is_valid ? (
              <ShieldCheck className="w-6 h-6 shrink-0" />
            ) : (
              <ShieldAlert className="w-6 h-6 shrink-0" />
            )}
            <div>
              <div className="font-bold text-xs uppercase">
                {verificationStatus?.is_valid ? 'EVIDENCE INTEGRITY VERIFIED' : 'TAMPER DETECTED!'}
              </div>
              <div className="text-[10px] opacity-80 truncate max-w-[200px]">
                {verificationStatus?.is_valid ? 'SHA-256 Digest Match Confirmed' : 'Cryptographic Hash Mismatch'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Technical & Forensic Attributes */}
        <div className="lg:col-span-2 space-y-6">
          {/* Transaction Metadata Card */}
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-3 flex items-center justify-between">
              <span>Cryptocurrency Transaction Parameters</span>
              <span className="text-[10px] text-slate-400">Schema v1.0.0</span>
            </h2>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-3 rounded border border-slate-800">
              <div>
                <span className="text-slate-400 block text-[10px]">SOURCE WALLET</span>
                <span className="text-slate-200 font-bold truncate block">{evidence.source_wallet}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">DESTINATION WALLET</span>
                <span className="text-slate-200 font-bold truncate block">{evidence.destination_wallet}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">TRANSFER AMOUNT</span>
                <span className="text-white font-bold">{evidence.amount?.toFixed(4)} BTC</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">EVENT TIMESTAMP</span>
                <span className="text-slate-300">{evidence.event_timestamp || 'N/A'}</span>
              </div>
            </div>

            {/* AI Uncertainty & Multi-Signal Gauges */}
            <div className="grid grid-cols-3 gap-3 mt-3 bg-slate-950 p-3 rounded border border-slate-800">
              <div>
                <span className="text-slate-400 block text-[10px]">MODEL RISK (RF)</span>
                <span className="text-orange-400 font-bold text-sm">{evidence.risk_score?.toFixed(4)}</span>
                <span className="text-[10px] text-slate-400 block">&plusmn;{evidence.uncertainty_delta?.toFixed(4)} ({evidence.confidence})</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">ANOMALY SCORE (IFOREST)</span>
                <span className="text-purple-400 font-bold text-sm">{evidence.anomaly_score?.toFixed(4)}</span>
                <span className="text-[10px] text-slate-400 block">Topological Outlier</span>
              </div>
              <div>
                <span className="text-slate-400 block text-[10px]">CORROBORATION</span>
                <span className="text-blue-400 font-bold text-sm">{corrob.status || 'MODERATE'}</span>
                <span className="text-[10px] text-slate-400 block">{corrob.supporting_indicator_count || 2} indicators</span>
              </div>
            </div>
          </div>

          {/* SHAP Feature Explanations */}
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-3 flex items-center justify-between">
              <span>SHAP Decision Attributions (Why Flagged?)</span>
              <span className="text-[10px] text-purple-400 font-bold">EXPLANATORY TRUST</span>
            </h2>

            <div className="space-y-2">
              {expl.top_positive_contributors?.map((driver: any, idx: number) => (
                <div key={idx} className="p-2.5 bg-slate-950 rounded border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-red-400 font-bold mr-2">+{(driver.shap_value || 0).toFixed(4)}</span>
                    <span className="text-slate-200 font-semibold">{driver.display_name}</span>
                    <span className="text-slate-400 ml-2 text-[10px]">(Observed Value: {driver.feature_value})</span>
                  </div>
                  <span className="text-[10px] text-red-400/80 uppercase font-bold">INCREASES RISK</span>
                </div>
              ))}
              {(!expl.top_positive_contributors || expl.top_positive_contributors.length === 0) && (
                <div className="p-4 text-center text-slate-400">Baseline risk profile. No abnormal drivers detected.</div>
              )}
            </div>
          </div>

          {/* Canonical JSON Record & SHA-256 Digest */}
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-xs font-bold uppercase text-slate-200">
                Canonical Evidence Record & SHA-256 Digest
              </h2>
              <button
                onClick={copyCanonicalJson}
                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded flex items-center gap-1 text-[11px]"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied' : 'Copy Canonical JSON'}
              </button>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded mb-3">
              <div className="text-[10px] text-slate-400 uppercase">SHA-256 INTEGRITY DIGEST</div>
              <div className="text-emerald-400 font-bold break-all">{evidence.integrity_digest}</div>
            </div>

            <pre className="bg-slate-950 p-3 rounded border border-slate-800 text-[11px] text-slate-300 overflow-x-auto max-h-48">
              {JSON.stringify({
                evidence_id: evidence.evidence_id,
                case_id: evidence.case_id,
                transaction_id: evidence.transaction_id,
                source_wallet: evidence.source_wallet,
                destination_wallet: evidence.destination_wallet,
                amount: evidence.amount,
                model_id: evidence.model_id,
                model_version: evidence.model_version,
                risk_score: evidence.risk_score,
                anomaly_score: evidence.anomaly_score,
                confidence: evidence.confidence,
                uncertainty_delta: evidence.uncertainty_delta,
                integrity_digest: evidence.integrity_digest
              }, null, 2)}
            </pre>
          </div>
        </div>

        {/* Right Col: Interactive Tamper Sandbox, Blockchain Anchor, & Human Review */}
        <div className="space-y-6">
          {/* Tamper Simulation Sandbox */}
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-2 flex items-center gap-1.5 text-rose-400">
              <ShieldAlert className="w-4 h-4" />
              Cryptographic Tamper Sandbox
            </h2>
            <p className="text-[11px] text-slate-400 mb-3 font-sans">
              Inject a deliberate modification into the evidence payload to verify mathematical tamper detection.
            </p>

            <div className="space-y-3">
              <div>
                <label className="block text-slate-400 text-[10px] mb-1">MUTATE AMOUNT VALUE (BTC)</label>
                <input
                  type="number"
                  step="0.1"
                  value={tamperAmount}
                  onChange={(e) => setTamperAmount(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-rose-500"
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleSimulateTamper}
                  disabled={isTamperingLoading}
                  className="flex-1 py-1.5 bg-rose-950 hover:bg-rose-900 text-rose-200 border border-rose-800 rounded font-semibold text-center"
                >
                  Inject Tamper
                </button>
                <button
                  onClick={handleRestoreEvidence}
                  disabled={isTamperingLoading}
                  className="flex-1 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-semibold text-center border border-slate-700 flex items-center justify-center gap-1"
                >
                  <RotateCcw className="w-3 h-3" /> Restore
                </button>
              </div>

              <button
                onClick={handleVerify}
                className="w-full py-1.5 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 rounded font-semibold"
              >
                Re-Verify Digest
              </button>
            </div>
          </div>

          {/* Blockchain Smart Contract Anchor */}
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-2 flex items-center gap-1.5 text-blue-400">
              <Blocks className="w-4 h-4" />
              Blockchain Evidence Anchor
            </h2>
            <p className="text-[11px] text-slate-400 mb-3 font-sans">
              Anchors cryptographic SHA-256 digest on-chain for tamper-evident public immutability.
            </p>

            {evidence.is_anchored ? (
              <div className="p-3 bg-slate-950 rounded border border-slate-800 space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400 text-[10px]">ANCHOR STATUS</span>
                  <span className="text-emerald-400 font-bold">CONFIRMED</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400 text-[10px]">BLOCK NUMBER</span>
                  <span className="text-white font-bold">#{evidence.blockchain_block}</span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] block">TRANSACTION HASH</span>
                  <span className="text-blue-400 break-all text-[10px]">{evidence.blockchain_tx_hash}</span>
                </div>
              </div>
            ) : (
              <button
                onClick={handleAnchorToBlockchain}
                className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-semibold flex items-center justify-center gap-1.5 shadow-sm shadow-blue-950"
              >
                <Blocks className="w-3.5 h-3.5" /> Anchor Digest to Smart Contract
              </button>
            )}
          </div>

          {/* Mandatory Human Analyst Review */}
          <div className="bg-navy-900 border border-forensic-border rounded-lg p-5">
            <h2 className="text-xs font-bold uppercase text-slate-200 mb-2 flex items-center gap-1.5 text-purple-400">
              <UserCheck className="w-4 h-4" />
              Human Analyst Review & Findings
            </h2>
            <p className="text-[11px] text-slate-400 mb-3 font-sans">
              Promote AI lead to verified forensic finding with documented rationale.
            </p>

            <form onSubmit={handleSubmitReview} className="space-y-3">
              <div>
                <label className="block text-slate-400 text-[10px] mb-1">PROMOTED STATUS</label>
                <select
                  value={reviewState}
                  onChange={(e) => setReviewState(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="FORENSIC_FINDING">FORENSIC_FINDING (Promoted Lead)</option>
                  <option value="UNDER_REVIEW">UNDER_REVIEW (Pending Additional Evidence)</option>
                  <option value="ESCALATED">ESCALATED (High-Priority Case Escalation)</option>
                  <option value="REJECTED">REJECTED (Benign False Positive)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 text-[10px] mb-1">FINDING SUMMARY</label>
                <textarea
                  value={reviewSummary}
                  onChange={(e) => setReviewSummary(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white focus:outline-none focus:border-purple-500 font-sans text-xs h-16"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 text-[10px] mb-1">CORROBORATIVE RATIONALE</label>
                <textarea
                  value={reviewRationale}
                  onChange={(e) => setReviewRationale(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white focus:outline-none focus:border-purple-500 font-sans text-xs h-16"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 bg-purple-600 hover:bg-purple-500 text-white rounded font-semibold"
              >
                Record Finding & Append Custody Hash
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
