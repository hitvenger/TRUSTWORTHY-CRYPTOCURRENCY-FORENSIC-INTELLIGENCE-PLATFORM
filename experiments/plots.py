"""
Academic Forensic Validation & Visualization Plotter for TCF-FX.

Generates publication-quality figures:
1. ROC Curves (Receiver Operating Characteristic)
2. Precision-Recall (PR) Curves
3. Reliability / Calibration Curves
4. Confusion Matrix Heatmaps
5. Top Feature Importance Rankings
6. Ablation Comparison Bar Charts
"""

import os
import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.calibration import calibration_curve


def ensure_fig_dir(output_dir: str = "reports/figures") -> str:
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def plot_roc_curve(y_true: np.ndarray, y_scores: np.ndarray, model_name: str, run_id: str, output_path: str):
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    plt.figure(figsize=(7, 6), dpi=150)
    plt.plot(fpr, tpr, color="#2563eb", lw=2, label=f"{model_name}")
    plt.plot([0, 1], [0, 1], color="#94a3b8", linestyle="--", lw=1.5, label="Random Classifier (AUC = 0.50)")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (FPR)", fontsize=11, fontweight="bold")
    plt.ylabel("True Positive Rate (TPR / Recall)", fontsize=11, fontweight="bold")
    plt.title(f"ROC Curve — {model_name}\n(Dataset Run: {run_id})", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_pr_curve(y_true: np.ndarray, y_scores: np.ndarray, model_name: str, run_id: str, output_path: str):
    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    plt.figure(figsize=(7, 6), dpi=150)
    plt.plot(recall, precision, color="#059669", lw=2, label=f"{model_name}")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("Recall", fontsize=11, fontweight="bold")
    plt.ylabel("Precision", fontsize=11, fontweight="bold")
    plt.title(f"Precision-Recall Curve — {model_name}\n(Dataset Run: {run_id})", fontsize=12, fontweight="bold")
    plt.legend(loc="lower left")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_calibration_curve(y_true: np.ndarray, y_scores: np.ndarray, model_name: str, run_id: str, output_path: str):
    prob_true, prob_pred = calibration_curve(y_true, y_scores, n_bins=10)
    plt.figure(figsize=(7, 6), dpi=150)
    plt.plot(prob_pred, prob_true, "s-", color="#7c3aed", lw=2, label=f"{model_name}")
    plt.plot([0, 1], [0, 1], color="#94a3b8", linestyle="--", lw=1.5, label="Perfect Calibration")
    plt.xlabel("Mean Predicted Probability", fontsize=11, fontweight="bold")
    plt.ylabel("Fraction of True Illicit Positives", fontsize=11, fontweight="bold")
    plt.title(f"Calibration Reliability Curve — {model_name}\n(Dataset Run: {run_id})", fontsize=12, fontweight="bold")
    plt.legend(loc="upper left")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_confusion_matrix(cm_dict: Dict[str, int], model_name: str, run_id: str, output_path: str):
    tp = cm_dict.get("true_positives", 0)
    fp = cm_dict.get("false_positives", 0)
    tn = cm_dict.get("true_negatives", 0)
    fn = cm_dict.get("false_negatives", 0)

    matrix = np.array([[tn, fp], [fn, tp]])
    plt.figure(figsize=(6, 5), dpi=150)
    plt.imshow(matrix, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(f"Confusion Matrix — {model_name}\n(Dataset Run: {run_id})", fontsize=12, fontweight="bold")
    plt.colorbar()
    tick_marks = [0, 1]
    plt.xticks(tick_marks, ["Licit (0)", "Illicit (1)"], fontweight="bold")
    plt.yticks(tick_marks, ["Licit (0)", "Illicit (1)"], fontweight="bold")

    thresh = matrix.max() / 2.0
    for i in range(2):
        for j in range(2):
            plt.text(j, i, f"{matrix[i, j]:,}", horizontalalignment="center",
                     color="white" if matrix[i, j] > thresh else "black", fontweight="bold")

    plt.ylabel("Actual Label", fontsize=11, fontweight="bold")
    plt.xlabel("Predicted Label", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_feature_importances(importances: Dict[str, float], run_id: str, output_path: str, top_n: int = 12):
    sorted_feats = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:top_n]
    names = [f[0] for f in reversed(sorted_feats)]
    scores = [f[1] for f in reversed(sorted_feats)]

    plt.figure(figsize=(9, 6), dpi=150)
    plt.barh(range(len(names)), scores, color="#0284c7")
    plt.yticks(range(len(names)), names, fontsize=9)
    plt.xlabel("Gini Feature Importance / Weight", fontsize=11, fontweight="bold")
    plt.title(f"Top {top_n} Forensic Feature Importances\n(Dataset Run: {run_id})", fontsize=12, fontweight="bold")
    plt.grid(axis="x", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
