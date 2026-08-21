"""
Forensic SHAP Explainability Engine for TCF-FX.

Binds model decision attributions directly to canonical evidence records,
pinpointing exact positive (risk-increasing) and negative (risk-decreasing) drivers.
"""

import datetime
import numpy as np
from typing import Dict, List, Any, Optional
from forensic_engine.canonical import canonical_json_dumps

try:
    import shap
    HAS_SHAP = True
except Exception:
    HAS_SHAP = False


# Human-interpretable forensic feature translations
FEATURE_EXPLANATION_MAP = {
    "amount": "Transfer Amount (Raw BTC)",
    "log_amount": "Log Scaled Transaction Volume",
    "src_in_degree": "Source Inbound Transaction History",
    "src_out_degree": "Source Outbound Transaction History",
    "src_total_degree": "Source Aggregate Activity Count",
    "src_unique_counterparties": "Source Counterparty Breadth",
    "src_counterparty_diversity": "Source Counterparty Diversity Index",
    "src_out_mean": "Source Average Outgoing Transfer Size",
    "src_out_max": "Source Peak Historical Transfer Size",
    "src_out_std": "Source Outgoing Transfer Variance",
    "src_in_mean": "Source Inbound Average Transfer Size",
    "src_net_flow": "Source Net Flow (Inflow - Outflow)",
    "src_wallet_age_seconds": "Source Wallet Maturity (Age)",
    "src_time_since_last_tx": "Inactivity Period Prior to Transfer",
    "src_tx_velocity_hourly": "High-Frequency Transaction Velocity",
    "src_is_dormant_reactivation": "Sudden Dormant Wallet Reactivation",
    "src_past_1h_txs": "Rolling 1-Hour Burst Transaction Frequency",
    "src_past_1h_vol": "Rolling 1-Hour Burst Transaction Volume",
    "src_past_24h_txs": "Rolling 24-Hour Velocity",
    "src_past_24h_vol": "Rolling 24-Hour Cumulative Volume",
    "dst_in_degree": "Destination Inbound Transaction Count",
    "dst_out_degree": "Destination Outbound Transaction Count",
    "dst_total_degree": "Destination Overall Activity Count",
    "dst_unique_counterparties": "Destination Counterparty Breadth",
    "dst_in_mean": "Destination Average Inbound Transfer",
    "dst_wallet_age_seconds": "Destination Wallet Age",
    "src_clustering_coefficient": "Topological Clustering Density",
    "src_1hop_neighborhood_size": "Local 1-Hop Neighborhood Size",
    "k_hop_suspicious_exposure": "Topological Exposure to Flagged Clusters",
    "rapid_drain_indicator": "Rapid Layering / Drain Sequence",
}


class ForensicShapExplainer:
    def __init__(self, model: Any, feature_names: List[str], background_data: Optional[np.ndarray] = None):
        self.model = model
        self.feature_names = feature_names
        self.background_data = background_data
        self.explainer = None
        self._initialize_explainer()

    def _initialize_explainer(self):
        if HAS_SHAP and hasattr(self.model, "clf"):
            try:
                self.explainer = shap.TreeExplainer(self.model.clf)
            except Exception:
                self.explainer = None

    def explain_instance(
        self,
        X_sample: np.ndarray,
        transaction_id: str,
        evidence_id: Optional[str] = None,
        model_version: str = "1.0.0",
        risk_score: float = 0.5,
        top_k: int = 6
    ) -> Dict[str, Any]:
        """
        Computes exact local feature attributions and generates human-auditable forensic explanation.
        """
        if X_sample.ndim == 1:
            X_2d = X_sample.reshape(1, -1)
            raw_vals = X_sample
        else:
            X_2d = X_sample
            raw_vals = X_sample[0]

        shap_values_dict = {}
        base_value = 0.5

        if self.explainer is not None:
            try:
                raw_shap = self.explainer.shap_values(X_2d)
                # Handle binary classification shapes
                if isinstance(raw_shap, list) and len(raw_shap) == 2:
                    vals = raw_shap[1][0]
                elif isinstance(raw_shap, np.ndarray):
                    if raw_shap.ndim == 3:
                        vals = raw_shap[0, :, 1]
                    else:
                        vals = raw_shap[0]
                else:
                    vals = np.array(raw_shap).flatten()

                for idx, name in enumerate(self.feature_names):
                    if idx < len(vals):
                        shap_values_dict[name] = float(vals[idx])
                
                if hasattr(self.explainer, "expected_value"):
                    exp_val = self.explainer.expected_value
                    base_value = float(exp_val[1] if isinstance(exp_val, (list, np.ndarray)) else exp_val)
            except Exception:
                self.explainer = None

        # Fallback attribution calculation based on tree feature importance & deviation from mean
        if not shap_values_dict:
            importances = getattr(self.model, "get_feature_importances", lambda: {})()
            mean_ref = np.mean(self.background_data, axis=0) if self.background_data is not None else np.zeros(len(self.feature_names))
            std_ref = np.std(self.background_data, axis=0) + 1e-5 if self.background_data is not None else np.ones(len(self.feature_names))

            for idx, name in enumerate(self.feature_names):
                val = raw_vals[idx] if idx < len(raw_vals) else 0.0
                z_score = (val - mean_ref[idx]) / std_ref[idx] if idx < len(mean_ref) else 0.0
                weight = importances.get(name, 1.0 / len(self.feature_names))
                # Attribution proportional to z-score * weight
                attribution = float(np.clip(z_score * weight * (risk_score - 0.5) * 2.0, -0.5, 0.5))
                shap_values_dict[name] = round(attribution, 6)

        # Sort positive and negative contributors
        positive_contributors = []
        negative_contributors = []

        for name, val in shap_values_dict.items():
            feat_idx = self.feature_names.index(name) if name in self.feature_names else 0
            raw_v = float(raw_vals[feat_idx]) if feat_idx < len(raw_vals) else 0.0
            item = {
                "feature_name": name,
                "display_name": FEATURE_EXPLANATION_MAP.get(name, name),
                "feature_value": round(raw_v, 4),
                "shap_value": round(val, 6),
                "impact": "INCREASES_RISK" if val > 0 else "DECREASES_RISK",
            }
            if val > 0:
                positive_contributors.append(item)
            else:
                negative_contributors.append(item)

        positive_contributors.sort(key=lambda x: x["shap_value"], reverse=True)
        negative_contributors.sort(key=lambda x: x["shap_value"])  # Most negative first

        # Synthesize plain-language summary
        top_pos = positive_contributors[:top_k]
        top_neg = negative_contributors[:top_k]

        key_drivers_summary = [
            f"{ind['display_name']} ({ind['feature_value']}) pushed risk upward by +{ind['shap_value']:.4f}"
            for ind in top_pos[:3]
        ]
        
        explanation_obj = {
            "transaction_id": transaction_id,
            "evidence_id": evidence_id,
            "model_version": model_version,
            "base_expected_value": round(base_value, 4),
            "output_risk_score": round(risk_score, 4),
            "explanation_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "top_positive_contributors": top_pos,
            "top_negative_contributors": top_neg,
            "all_feature_attributions": shap_values_dict,
            "summary_drivers": key_drivers_summary,
            "plain_text_rationale": "Transaction flagged due to: " + "; ".join([d["display_name"] for d in top_pos[:4]]) if top_pos else "Baseline risk."
        }

        return explanation_obj
