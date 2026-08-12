# SkillSync System Architecture & Design Decisions

This document details the architectural layout, core design choices, and file structure of the SkillSync platform.

---

## 🏗️ Project File Structure

```
skillsync/
├── config/                    # Django configuration & settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── resumes/               # Resume upload, parsing, models
│   ├── jobs/                  # Job description models & views
│   ├── matching/              # Core matching logic & services
│   ├── evaluation/            # Validation sets & benchmarking
│   └── users/                 # Authentication & profiles
├── skills_taxonomy/           # Curated skill dictionary & loaders
│   ├── skills.json
│   └── loaders.py
├── docs/                      # Extended project documentation
│   ├── API.md
│   ├── ROADMAP.md
│   └── ARCHITECTURE.md
├── tests/                     # Unit & integration tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── manage.py
└── README.md
```

---

## 💡 Key Design & Architecture Decisions

1. **Why spaCy + PhraseMatcher over generic Named Entity Recognition (NER)?**
   - Pre-trained generic NER models (like `en_core_web_sm`) are tuned for location, person, or organization entities rather than technical skill taxonomies. 
   - Combining `spaCy`'s `PhraseMatcher` with a curated skills taxonomy provides faster execution, deterministic extraction, and complete transparency.

2. **Why `pgvector` over dedicated Vector Databases (e.g., Pinecone/Chroma)?**
   - Keeping vector embeddings inside PostgreSQL reduces operational overhead and system complexity during early-to-mid stage scale.
   - SQL queries can combine structured filters (e.g., location, experience) with vector similarity searches directly in single transactions.

3. **Skill-Level Granularity vs. Full-Document Embeddings**
   - Document-level embeddings reflect general context but fail to provide actionable feedback.
   - SkillSync embeds and compares individual extracted skills to deliver granular, explainable match feedback (identifying matched skills vs. missing gap skills).
