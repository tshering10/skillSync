# SkillSync API Documentation (Phase 1)

This document details the REST API endpoints available for the SkillSync backend service.

---

## Base URL
`http://localhost:8000/api/`

---

## Endpoints

### 1. Upload & Parse Resume

Upload a candidate resume in PDF or DOCX format for parsing and skill extraction.

- **Method:** `POST`
- **URL:** `/api/resumes/`
- **Content-Type:** `multipart/form-data`

#### Request Body
```json
{
  "file": "<binary PDF or DOCX file>"
}
```

#### Response (`201 Created`)
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "uploaded",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 2. Create Job Description

Create a target job description to match against resumes.

- **Method:** `POST`
- **URL:** `/api/jobs/`
- **Content-Type:** `application/json`

#### Request Body
```json
{
  "title": "Backend Developer",
  "company": "Acme Corp",
  "raw_text": "We're looking for a Django developer with 2+ years experience in REST APIs, PostgreSQL, and Docker..."
}
```

#### Response (`201 Created`)
```json
{
  "id": "8c59f91a-7b3b-4199-a681-42ab2374e2d3",
  "title": "Backend Developer",
  "company": "Acme Corp",
  "created_at": "2024-01-15T10:31:00Z"
}
```

---

### 3. Match Resume to Job

Analyze semantic and keyword skill similarity between a resume and job description.

- **Method:** `POST`
- **URL:** `/api/matching/`
- **Content-Type:** `application/json`

#### Request Body
```json
{
  "resume_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "job_description_id": "8c59f91a-7b3b-4199-a681-42ab2374e2d3"
}
```

#### Response (`200 OK`)
```json
{
  "id": "e9b418fa-3467-4221-9e20-94fb28859139",
  "match_score": 72.5,
  "matched_skills": {
    "Django": 0.94,
    "REST APIs": 0.91,
    "PostgreSQL": 0.88
  },
  "missing_skills": {
    "Docker": 0.82,
    "Kubernetes": 0.76
  },
  "explanation": "Strong match on core backend skills. Consider adding containerization experience (Docker)."
}
```
