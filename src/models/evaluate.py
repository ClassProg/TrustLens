
import csv
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, roc_auc_score


CSV_FIELDS = [
    "timestamp",
    "checkpoint_path",
    "architecture",
    "crop_optic_disc",
    "crop_fraction",
    "image_size",
    "num_images",
    "threshold",
    "accuracy",
    "sensitivity",
    "specificity",
    "balanced_accuracy",
    "precision",
    "f1_score",
    "sensitivity_x_specificity",
    "auroc",
    "auprc",
    "tp",
    "tn",
    "fp",
    "fn",
    "selection",
]


def calculate_metrics(labels, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)

    tp = int(np.sum((predictions == 1) & (labels == 1)))
    tn = int(np.sum((predictions == 0) & (labels == 0)))
    fp = int(np.sum((predictions == 1) & (labels == 0)))
    fn = int(np.sum((predictions == 0) & (labels == 1)))

    sensitivity = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    accuracy = (tp + tn) / len(labels) if len(labels) else 0.0

    balanced_accuracy = (sensitivity + specificity) / 2
    f1_score = (
        2 * tp / (2 * tp + fp + fn)
        if (2 * tp + fp + fn)
        else 0.0
    )

    return {
        "threshold": round(float(threshold), 2),
        "accuracy": accuracy,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "balanced_accuracy": balanced_accuracy,
        "precision": precision,
        "f1_score": f1_score,
        "sensitivity_x_specificity": sensitivity * specificity,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def find_best_thresholds(results, minimum_sensitivity=0.90):
    best = {
        "best_balanced_accuracy": max(
            results,
            key=lambda r: (
                r["balanced_accuracy"],
                r["sensitivity"],
                r["specificity"],
            ),
        ),
        "best_f1": max(
            results,
            key=lambda r: r["f1_score"],
        ),
        "best_sensitivity_x_specificity": max(
            results,
            key=lambda r: r["sensitivity_x_specificity"],
        ),
    }

    eligible = [
        result
        for result in results
        if result["sensitivity"] >= minimum_sensitivity
    ]

    best["specificity_at_90_sensitivity"] = (
        max(
            eligible,
            key=lambda r: (
                r["specificity"],
                r["sensitivity"],
            ),
        )
        if eligible
        else None
    )

    return best


def save_results_csv(results, cfg, checkpoint_path, auroc, auprc, best):
    output_path = Path(
        cfg.get("evaluation", {}).get(
            "results_csv",
            "models/outputs/evaluations/model_results.csv",
        )
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = output_path.exists() and output_path.stat().st_size > 0

    checkpoint_path = str(Path(checkpoint_path).resolve())
    timestamp = datetime.now(timezone.utc).isoformat()

    selections = {}
    for name, result in best.items():
        if result is not None:
            selections.setdefault(result["threshold"], []).append(name)

    with output_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)

        if not file_exists:
            writer.writeheader()

        for result in results:
            row = {
                "timestamp": timestamp,
                "checkpoint_path": checkpoint_path,
                "architecture": cfg["model"]["architecture"],
                "crop_optic_disc": cfg["data"].get(
                    "crop_optic_disc", True
                ),
                "crop_fraction": cfg["data"].get(
                    "crop_fraction", 0.45
                ),
                "image_size": cfg["data"]["image_size"],
                "num_images": result["tp"] + result["tn"]
                + result["fp"] + result["fn"],
                **result,
                "auroc": auroc,
                "auprc": auprc,
                "selection": ";".join(
                    selections.get(result["threshold"], [])
                ),
            }
            writer.writerow(row)

    return output_path


def print_result(label, result):
    if result is None:
        print(f"{label}: No qualifying threshold found.")
        return

    print(
        f"{label} | "
        f"Threshold: {result['threshold']:.2f} | "
        f"Accuracy: {result['accuracy']:.2%} | "
        f"Sensitivity: {result['sensitivity']:.2%} | "
        f"Specificity: {result['specificity']:.2%} | "
        f"Balanced Acc: {result['balanced_accuracy']:.2%} | "
        f"Precision: {result['precision']:.2%} | "
        f"F1: {result['f1_score']:.2%} | "
        f"TP={result['tp']}, TN={result['tn']}, "
        f"FP={result['fp']}, FN={result['fn']}"
    )


def evaluate_model(model, val_loader, device, cfg, checkpoint_path):
    model.to(device)
    model.eval()

    all_labels = []
    all_probs = []

    with torch.no_grad():
        for images, labels, _ in val_loader:
            images = images.to(device)

            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)[:, 1]

            all_labels.extend(labels.cpu().tolist())
            all_probs.extend(probs.cpu().tolist())

    labels = np.asarray(all_labels, dtype=int)
    probabilities = np.asarray(all_probs, dtype=float)

    if len(labels) == 0:
        raise ValueError("Validation dataset is empty.")

    if len(np.unique(labels)) < 2:
        raise ValueError(
            "AUROC requires both glaucoma and non-glaucoma "
            "images in the validation dataset."
        )

    auroc = roc_auc_score(labels, probabilities)
    auprc = average_precision_score(labels, probabilities)

    thresholds = np.round(np.arange(0.05, 0.951, 0.01), 2)

    results = [
        calculate_metrics(labels, probabilities, threshold)
        for threshold in thresholds
    ]

    best = find_best_thresholds(results)

    print(f"\nImages evaluated: {len(labels)}")
    print(f"AUROC: {auroc:.4f}")
    print(f"AUPRC: {auprc:.4f}")

    print("\n--- Best Thresholds ---")
    print_result(
        "Best balanced accuracy",
        best["best_balanced_accuracy"],
    )
    print_result(
        "Best F1-score",
        best["best_f1"],
    )
    print_result(
        "Best sensitivity x specificity",
        best["best_sensitivity_x_specificity"],
    )
    print_result(
        "Best specificity with >=90% sensitivity",
        best["specificity_at_90_sensitivity"],
    )

    print("\n--- Standard Thresholds ---")
    for threshold in [0.30, 0.40, 0.50, 0.60, 0.70]:
        result = next(
            r for r in results
            if abs(r["threshold"] - threshold) < 1e-9
        )
        print_result("Standard", result)

    csv_path = save_results_csv(
        results, cfg, checkpoint_path, auroc, auprc, best
    )

    print(f"\nEvaluation results saved to: {csv_path}")

    return {
        "auroc": auroc,
        "auprc": auprc,
        "best_thresholds": best,
        "csv_path": str(csv_path),
    }
