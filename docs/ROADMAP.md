# SkillSync Roadmap & Project Lifecycle

This document tracks current progress, planned phases, known limitations, and recent changes for SkillSync.

---

## 🗺️ Project Roadmap

### Phase 1 — Core MVP (Weeks 1–3)
- [x] Resume & JobDescription models
- [x] File upload & text extraction (PDF/DOCX)
- [x] Skill extraction pipeline (spaCy + Taxonomy)
- [x] Embedding generation (`sentence-transformers`)
- [x] Matching & similarity computation
- [x] Core REST API endpoints

### Phase 2 — Validation (Week 4)
- [x] Build evaluation set (20–30 labeled resume/JD pairs)
- [x] Matcher evaluation script (`evaluate_matcher.py`)
- [x] Analyze failure cases & tune thresholds
- [x] Document benchmark findings (`docs/BENCHMARK.md`)

### Phase 3 — Production Hardening (Weeks 5–6)
- [ ] Move parsing/embedding to Celery tasks
- [ ] Redis caching for embeddings
- [ ] Comprehensive unit & integration tests
- [ ] GitHub Actions CI/CD setup
- [x] OpenAPI documentation (`drf-spectacular`) (`/api/docs/`, `/api/redoc/`)
- [x] Security audit: File size & extension validation (5MB limit, disallowed extensions)

### Phase 4 — Differentiators & AI Generation (Week 7+)
- [ ] **LLM Integration (OpenAI / Gemini API):** AI Feedback & Personalized Advice Generator based on system skill extraction results
- [ ] **AI Resume Rewriter:** Tailor resume bullet points specifically to job descriptions
- [ ] Score history tracking (re-upload iterations)
- [ ] Bilingual/Nepali resume support
- [ ] React/Next.js frontend interface

---

## ⚠️ Known Limitations

### MVP Limitations
- **Scanned/image-based resumes:** OCR is not currently integrated; resumes must have selectable text.
- **Legacy `.doc` format:** Only `.docx` is supported.
- **Multi-column layouts:** Text extraction may interleave columns.
- **Synchronous processing:** Initial upload currently blocks until parsing finishes (addressed in Phase 3 async tasks).

---

## 📜 Changelog

### Unreleased (Phase 1)
- Initial project setup (Django + DRF)
- Resume upload & document parsing
- Skill extraction pipeline & embeddings
- Matching endpoint & scoring logic
- Modularized project documentation (`docs/`)
