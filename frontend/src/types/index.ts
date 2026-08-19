export interface Case {
  case_id: string;
  title: string;
  description?: string;
  investigator: string;
  status: 'ACTIVE' | 'UNDER_REVIEW' | 'CLOSED' | 'ARCHIVED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  tags: string[];
  evidence_count?: number;
  high_risk_lead_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface EvidenceItem {
  evidence_id: string;
  case_id: string;
  evidence_type: string;
  source: string;
  source_identifier?: string;
  acquisition_timestamp: string;
  event_timestamp?: string;
  transaction_id: string;
  source_wallet: string;
  destination_wallet: string;
  amount: number;
  feature_schema_version: string;
  model_id: string;
  model_version: string;
  risk_score: number;
  anomaly_score: number;
  graph_score: number;
  temporal_score: number;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  uncertainty_delta: number;
  explanation_json?: any;
  corroboration_json?: any;
  features_json?: any;
  analyst_status: 'MODEL_LEAD' | 'UNDER_REVIEW' | 'FORENSIC_FINDING' | 'REJECTED' | 'ESCALATED';
  analyst_comment?: string;
  analyst_name?: string;
  integrity_digest: string;
  is_tampered: boolean;
  blockchain_tx_hash?: string;
  blockchain_block?: number;
  is_anchored: boolean;
  created_at?: string;
}

export interface CustodyEvent {
  event_id: string;
  case_id: string;
  evidence_id?: string;
  actor: string;
  role: string;
  action: string;
  timestamp: string;
  metadata: Record<string, any>;
  previous_hash: string;
  event_hash: string;
}

export interface AnalystReview {
  review_id: string;
  case_id: string;
  evidence_id: string;
  transaction_id?: string;
  analyst_name: string;
  role: string;
  prior_state: string;
  new_state: string;
  finding_summary: string;
  rationale: string;
  corroborating_notes?: string;
  created_at?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  full_address: string;
  type: string;
  in_txs: number;
  out_txs: number;
  total_volume: number;
  max_risk: number;
  is_flagged: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  transaction_id: string;
  evidence_id: string;
  amount: number;
  risk_score: number;
  confidence: string;
  timestamp: string;
  analyst_status: string;
  is_tampered: boolean;
}

export interface DashboardSummary {
  metrics: {
    open_cases: number;
    total_evidence: number;
    high_risk_leads: number;
    critical_leads: number;
    integrity_tamper_alerts: number;
    analyst_review_queue: number;
    total_custody_events: number;
    confirmed_findings: number;
    anchored_on_chain: number;
  };
  risk_distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  recent_leads: EvidenceItem[];
}
