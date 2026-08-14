# 📊 SkillSync Matching Engine Benchmark Report
**Phase 2: Validation & Benchmarking**

*Date: August 2026*  
*Dataset: `apps/evaluation/dataset.json` (25 Labeled Pairs across 4 Categories)*  
*Engine: `apps.matching.services.calculate_match` (Sentence-Transformers + spaCy Canonical PhraseMatcher)*

---

## 📈 Benchmark Summary Table

| Metric | Baseline (Pre-Tuning) | Tuned (Canonical + Normalization) | Target | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Absolute Error (MAE)** | `7.05 pts` | **`6.24 pts`** | $< 8.0\text{ pts}$ | ✅ Passed |
| **Root Mean Squared Error (RMSE)** | `9.29 pts` | **`8.73 pts`** | $< 10.0\text{ pts}$ | ✅ Passed |
| **Pearson Correlation ($r$)** | `0.9560` | **`0.9612`** | $> 0.85$ | 🌟 Exceeded |
| **Accuracy ($\pm 10\text{ pt}$ tolerance)** | `76.0%` | **`76.0%`** | $> 70\%$ | ✅ Passed |
| **Accuracy ($\pm 15\text{ pt}$ tolerance)** | `88.0%` | **`92.0%`** | $> 85\%$ | ✅ Passed |
| **Average Latency per Pair** | $3,284\text{ ms}$ (cold download) | **$418.5\text{ ms}$** (cached) | $< 500\text{ ms}$ | ✅ Passed |

---

## 📑 Category Breakdown

```
Category             | Count | Avg Expected | Avg Predicted | MAE
--------------------------------------------------------------------
High Match           | 8     | 90.8         | 90.0          | 3.54 pts
Medium Match         | 7     | 58.7         | 54.9          | 9.69 pts
Low Match            | 6     | 12.7         | 12.4          | 2.72 pts
Edge Case            | 4     | 52.8         | 51.6          | 10.88 pts
```

---

## 🔍 Key Insights & Solved Issues

1. **High Match Convergence:**
   - With canonical skill normalization, High Match candidates are now scored at an average of **90.0%** (vs expected 90.8%), reducing MAE in this category to **3.54 pts**.
2. **Fixed Casing & Homonym Duplication:**
   - Synonyms like `RESTful APIs` $\leftrightarrow$ `REST API` and raw casing differences like `microservices` $\leftrightarrow$ `Microservices` are cleanly resolved to their canonical representations without generating duplicate entries.
3. **Strong Out-of-Domain Filtering:**
   - Low Match accuracy remains exceptional ($\text{MAE} = 2.72\text{ pts}$), guaranteeing that unqualified or unrelated profiles are appropriately filtered.

---

## ⚠️ Remaining Edge Cases for Future Iterations

1. **Linear Skill Decay (`pair_10`):** In cross-domain transitions (Data Analyst $\rightarrow$ ML), candidates possessing foundational programming skills (`Python`, `Pandas`) experience steep penalties when multi-faceted deep learning libraries are listed as requirements.
