# SkillSync — AI-Powered Resume-to-Job Matcher

A production-ready Django REST Framework service that analyzes how well candidate resumes match job descriptions using NLP skill extraction and semantic vector similarity (`pgvector` + `sentence-transformers`).

---

## ✨ Features

- 📄 **Resume Parsing:** PDF & DOCX text extraction.
- 🎯 **Skill Extraction:** Powered by spaCy NLP and a curated skill taxonomy.
- 🧠 **Semantic Matching:** Embeddings & cosine similarity matching beyond basic keyword search.
- 💡 **Explainable Results:** Clear breakdown of matched skills, missing skills, and match percentage.
- ⚡ **Production Ready:** Docker Compose, Celery + Redis task processing, and PostgreSQL + pgvector.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 6 + Django REST Framework |
| **Database** | PostgreSQL + pgvector |
| **Task Queue** | Celery + Redis |
| **NLP & Matching** | spaCy, sentence-transformers (`all-MiniLM-L6-v2`) |
| **Parsing** | pdfplumber, PyMuPDF, python-docx |
| **Auth** | SimpleJWT |
| **Containers** | Docker & Docker Compose |

---

## 🚀 Quick Start

### 1. Run with Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/tshering10/skillSync.git
cd skillsync

# Start services
docker-compose up --build

# Run database migrations
docker-compose exec web python manage.py migrate
```

Access the app:
- **API Base:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/

### 2. Local Setup (Without Docker)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations & start dev server
python manage.py migrate
python manage.py runserver
```

---

## 📚 Project Documentation

For deeper details, view our dedicated guides in `docs/`:

* 🔌 **[API Documentation](file:///c:/Users/LENOVO/Desktop/skillSync/docs/API.md)** — Complete REST API specifications & request/response payloads.
* 🏗️ **[Architecture & Design](file:///c:/Users/LENOVO/Desktop/skillSync/docs/ARCHITECTURE.md)** — System architecture, directory layout, and design decisions.
* 🗺️ **[Roadmap & Limitations](file:///c:/Users/LENOVO/Desktop/skillSync/docs/ROADMAP.md)** — Development roadmap, known limitations, and changelog.

---

## 🧪 Testing

```bash
pytest                 # Run test suite
pytest --cov          # Run tests with coverage report
```

---

## 📄 License

[MIT](LICENSE)