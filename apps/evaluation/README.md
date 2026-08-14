# 🧪 SkillSync Matching Engine Evaluation Suite

This directory contains the validation dataset, benchmarking runner, and analysis tools for evaluating the SkillSync matching algorithm against human-labeled ground truth.

---

## 📁 Directory Structure

```
apps/evaluation/
├── __init__.py
├── dataset.json           # 25 curated, labeled Resume + Job Description pairs
├── evaluate_matcher.py    # Benchmark runner script with MAE, RMSE, Pearson r metrics
└── README.md              # Documentation & benchmark guide
```

---

## 🚀 Running the Evaluation

To run the benchmark across the dataset:

```bash
# Standard summary report
python apps/evaluation/evaluate_matcher.py

# Verbose mode (shows match breakdown, skills, and latency for every pair)
python apps/evaluation/evaluate_matcher.py --verbose

# Export results to a JSON file
python apps/evaluation/evaluate_matcher.py --export-json docs/benchmark_results.json
```

---

## 📊 Evaluation Metrics

The script evaluates the scoring pipeline (`calculate_match`) across 4 key categories:
1. **High Match (80–100 pts):** Candidates with direct stack and domain overlap.
2. **Medium Match (50–79 pts):** Candidates with partial stack overlap or transitional skillsets.
3. **Low Match (0–49 pts):** Candidates from unrelated career fields.
4. **Edge Cases:** Testing keyword homonyms (e.g., *Java vs JavaScript*), keyword stuffing vs context, and synonyms.

### Key Metrics Tracked:
- **Mean Absolute Error (MAE):** Average point deviation from ground truth.
- **Root Mean Squared Error (RMSE):** Penalizes large prediction errors.
- **Pearson Correlation ($r$):** Alignment between predicted scores and expected rankings (target $> 0.85$).
- **Tolerance Bands:** Accuracy within $\pm 10$ points and $\pm 15$ points.
- **Latency (ms/pair):** Execution speed per resume-JD comparison.
