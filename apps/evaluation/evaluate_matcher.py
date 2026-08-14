#!/usr/bin/env python
"""
SkillSync - Matcher Evaluation & Benchmarking Script
Phase 2: Validation

Evaluates the matching engine (apps.matching.services.calculate_match) against
a curated ground-truth dataset of labeled Resume/Job pairs.

Usage:
    python apps/evaluation/evaluate_matcher.py
    python apps/evaluation/evaluate_matcher.py --verbose
    python apps/evaluation/evaluate_matcher.py --dataset path/to/dataset.json --export-json results.json
"""

import os
import sys
import json
import time
import math
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import matching engine components
try:
    from apps.matching.services import extract_skills_from_text, calculate_match
except ImportError as e:
    print(f"❌ Error importing matching services: {e}")
    sys.exit(1)


def compute_pearson_correlation(x, y):
    """Calculate Pearson correlation coefficient (r) between two numeric lists."""
    n = len(x)
    if n < 2:
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    variance_x = sum((val - mean_x) ** 2 for val in x)
    variance_y = sum((val - mean_y) ** 2 for val in y)

    if variance_x == 0 or variance_y == 0:
        return 0.0

    covariance = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    return covariance / (math.sqrt(variance_x) * math.sqrt(variance_y))


def evaluate_dataset(dataset_path, verbose=False, tolerance_narrow=10.0, tolerance_wide=15.0):
    """
    Run evaluation across all pairs in the dataset and return detailed metrics.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    results = []
    category_stats = {}
    total_start_time = time.perf_counter()

    for idx, pair in enumerate(pairs, 1):
        pair_id = pair.get("id", f"pair_{idx:02d}")
        category = pair.get("category", "Uncategorized")
        role_title = pair.get("role_title", "Unknown Role")
        resume_text = pair.get("resume_text", "")
        job_text = pair.get("job_text", "")
        expected_score = float(pair.get("expected_score", 0.0))

        start_time = time.perf_counter()

        # Step 1: Extract skills
        resume_skills = extract_skills_from_text(resume_text)
        job_skills = extract_skills_from_text(job_text)

        # Step 2: Compute match
        match_output = calculate_match(resume_text, job_text, resume_skills, job_skills)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        pred_score = float(match_output.get("match_score", 0.0))
        abs_error = abs(pred_score - expected_score)
        sq_error = abs_error ** 2

        is_within_narrow = abs_error <= tolerance_narrow
        is_within_wide = abs_error <= tolerance_wide

        pair_result = {
            "id": pair_id,
            "category": category,
            "role_title": role_title,
            "expected_score": expected_score,
            "predicted_score": pred_score,
            "abs_error": round(abs_error, 2),
            "sq_error": round(sq_error, 2),
            "within_narrow_tolerance": is_within_narrow,
            "within_wide_tolerance": is_within_wide,
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "matched_skills": list(match_output.get("matched_skills", {}).keys()),
            "missing_skills": list(match_output.get("missing_skills", {}).keys()),
            "explanation": match_output.get("explanation", ""),
            "latency_ms": round(elapsed_ms, 2),
            "notes": pair.get("notes", "")
        }
        results.append(pair_result)

        # Update category aggregates
        if category not in category_stats:
            category_stats[category] = {"errors": [], "predicted": [], "expected": [], "latencies": []}
        category_stats[category]["errors"].append(abs_error)
        category_stats[category]["predicted"].append(pred_score)
        category_stats[category]["expected"].append(expected_score)
        category_stats[category]["latencies"].append(elapsed_ms)

    total_time_ms = (time.perf_counter() - total_start_time) * 1000
    n = len(results)

    # Compute overall metrics
    all_abs_errors = [r["abs_error"] for r in results]
    all_sq_errors = [r["sq_error"] for r in results]
    all_preds = [r["predicted_score"] for r in results]
    all_expecteds = [r["expected_score"] for r in results]
    all_latencies = [r["latency_ms"] for r in results]

    mae = sum(all_abs_errors) / n if n else 0.0
    rmse = math.sqrt(sum(all_sq_errors) / n) if n else 0.0
    correlation = compute_pearson_correlation(all_preds, all_expecteds)
    narrow_acc = (sum(1 for r in results if r["within_narrow_tolerance"]) / n * 100) if n else 0.0
    wide_acc = (sum(1 for r in results if r["within_wide_tolerance"]) / n * 100) if n else 0.0
    avg_latency = sum(all_latencies) / n if n else 0.0

    category_summary = {}
    for cat, data in category_stats.items():
        cat_n = len(data["errors"])
        category_summary[cat] = {
            "count": cat_n,
            "mae": round(sum(data["errors"]) / cat_n, 2),
            "avg_expected": round(sum(data["expected"]) / cat_n, 1),
            "avg_predicted": round(sum(data["predicted"]) / cat_n, 1),
            "avg_latency_ms": round(sum(data["latencies"]) / cat_n, 1)
        }

    return {
        "dataset_path": str(dataset_path),
        "total_pairs": n,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "pearson_correlation": round(correlation, 4),
        "accuracy_within_10pt": round(narrow_acc, 1),
        "accuracy_within_15pt": round(wide_acc, 1),
        "avg_latency_ms": round(avg_latency, 2),
        "total_time_ms": round(total_time_ms, 2),
        "category_summary": category_summary,
        "results": results
    }


def print_report(eval_summary, verbose=False):
    """Format and print a professional CLI benchmark report."""
    print("=" * 80)
    print(" 🎯 SKILLSYNC - MATCHER BENCHMARK & EVALUATION REPORT")
    print("=" * 80)
    print(f" Dataset : {eval_summary['dataset_path']}")
    print(f" Samples : {eval_summary['total_pairs']} labeled pairs")
    print(f" Time    : {eval_summary['total_time_ms']} ms ({eval_summary['avg_latency_ms']} ms/pair)")
    print("-" * 80)
    print(" 📊 OVERALL ACCURACY METRICS:")
    print(f"  • Mean Absolute Error (MAE)   : {eval_summary['mae']} pts")
    print(f"  • Root Mean Squared Error (RMSE): {eval_summary['rmse']} pts")
    print(f"  • Pearson Correlation (r)     : {eval_summary['pearson_correlation']} (Target > 0.85)")
    print(f"  • Accuracy (±10 pt tolerance) : {eval_summary['accuracy_within_10pt']}%")
    print(f"  • Accuracy (±15 pt tolerance) : {eval_summary['accuracy_within_15pt']}%")
    print("-" * 80)

    # Category Breakdown
    print(" 📑 CATEGORY PERFORMANCE BREAKDOWN:")
    print(f"  {'Category':<20} | {'Count':<5} | {'Avg Expected':<12} | {'Avg Predicted':<13} | {'MAE':<8}")
    print("  " + "-" * 68)
    for cat, stats in eval_summary["category_summary"].items():
        print(f"  {cat:<20} | {stats['count']:<5} | {stats['avg_expected']:<12} | {stats['avg_predicted']:<13} | {stats['mae']:<8}")
    print("-" * 80)

    # Outliers / High Error Cases (|error| > 15 pts)
    outliers = [r for r in eval_summary["results"] if not r["within_wide_tolerance"]]
    print(f" ⚠️  OUTLIER CASES (Error > 15 pts): {len(outliers)}")
    if outliers:
        for item in outliers:
            print(f"   [{item['id']}] {item['role_title']} ({item['category']})")
            print(f"     Expected: {item['expected_score']}% | Predicted: {item['predicted_score']}% | Error: {item['abs_error']} pts")
            print(f"     Matched Skills : {', '.join(item['matched_skills']) or 'None'}")
            print(f"     Missing Skills : {', '.join(item['missing_skills']) or 'None'}")
            print(f"     Notes          : {item['notes']}")
            print()
    else:
        print("   🎉 None! All predictions are within the ±15 point margin.")
    print("-" * 80)

    if verbose:
        print(" 🔍 DETAILED PAIR-BY-PAIR BREAKDOWN:")
        for r in eval_summary["results"]:
            status_icon = "✅" if r["within_narrow_tolerance"] else ("⚠️" if r["within_wide_tolerance"] else "❌")
            print(f" {status_icon} [{r['id']}] {r['role_title']} [{r['category']}]")
            print(f"    Expected: {r['expected_score']:>5.1f}% | Predicted: {r['predicted_score']:>5.1f}% | Error: {r['abs_error']:>4.1f} pt | Latency: {r['latency_ms']} ms")
            print(f"    Matched: {', '.join(r['matched_skills']) or 'None'}")
            print(f"    Missing: {', '.join(r['missing_skills']) or 'None'}")
            print(f"    Explanation: {r['explanation']}")
            print()
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="SkillSync Matcher Validation & Benchmark Runner")
    default_dataset = PROJECT_ROOT / "apps" / "evaluation" / "dataset.json"
    parser.add_argument("--dataset", type=str, default=str(default_dataset), help="Path to evaluation dataset JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed breakdown for each pair")
    parser.add_argument("--export-json", type=str, help="Export benchmark output metrics to a JSON file")
    args = parser.parse_args()

    print("\n🚀 Running SkillSync Matcher Evaluation...")
    summary = evaluate_dataset(args.dataset, verbose=args.verbose)
    print_report(summary, verbose=args.verbose)

    if args.export_json:
        export_path = Path(args.export_json)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"💾 Benchmark results successfully exported to {export_path.resolve()}\n")


if __name__ == "__main__":
    main()
