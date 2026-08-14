import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer, util
from skills_taxonomy.loaders import get_all_skills, get_canonical_skill

# Load spaCy NLP model lazily
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

# Load SentenceTransformer model lazily
model = None

def get_sentence_transformer():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def extract_skills_from_text(text):
    """Extract skills using spaCy PhraseMatcher + Taxonomy matching with Canonical Normalization."""
    if not text:
        return []

    skills_list = get_all_skills()
    canonical_skills = set()

    if nlp:
        doc = nlp(text)
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(skill) for skill in skills_list]
        matcher.add("SKILL_MATCHER", patterns)

        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            canonical_name = get_canonical_skill(span.text)
            canonical_skills.add(canonical_name)

    # Fallback case-insensitive check
    text_lower = text.lower()
    for skill in skills_list:
        if skill.lower() in text_lower:
            canonical_name = get_canonical_skill(skill)
            canonical_skills.add(canonical_name)

    return sorted(list(canonical_skills))

def encode_document(text, transformer, chunk_size=1500, overlap=250):
    """
    Encodes full document text without truncating.
    For longer documents, splits text into overlapping windows and computes the mean pooled embedding.
    """
    if not text:
        return transformer.encode("", convert_to_tensor=True)

    text = text.strip()
    if len(text) <= chunk_size:
        return transformer.encode(text, convert_to_tensor=True)

    # Chunking long documents
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start += (chunk_size - overlap)

    # Encode all chunks and average
    chunk_embeddings = transformer.encode(chunks, convert_to_tensor=True)
    mean_embedding = chunk_embeddings.mean(dim=0, keepdim=True)
    # Unit normalize
    normalized_embedding = mean_embedding / mean_embedding.norm(dim=1, keepdim=True)
    return normalized_embedding.squeeze(0)

def calculate_match(resume_text, job_text, resume_skills, job_skills):
    """
    Computes match score combining:
    1. Skill overlap score with soft semantic partial credit (60% base weight)
    2. Document-level full semantic embedding similarity (40% base weight)
    3. Adaptive weight balancing for high-context / descriptive resumes
    """
    # Ensure all inputs are canonicalized
    resume_canonical = {get_canonical_skill(s) for s in (resume_skills or [])}
    job_canonical = {get_canonical_skill(s) for s in (job_skills or [])}

    resume_skills_lower = {s.lower(): s for s in resume_canonical}
    job_skills_lower = {s.lower(): s for s in job_canonical}

    matched_skills = {}
    missing_skills = {}
    matched_points = 0.0

    if job_skills_lower:
        matched_keys = set(resume_skills_lower.keys()).intersection(set(job_skills_lower.keys()))
        missing_keys = set(job_skills_lower.keys()) - set(resume_skills_lower.keys())

        # Exact matches get full credit (1.0 point each)
        for key in matched_keys:
            canonical_name = job_skills_lower[key]
            matched_skills[canonical_name] = 0.95
            matched_points += 1.0

        # Check missing skills for semantic partial matches (e.g. MySQL vs PostgreSQL)
        if missing_keys and resume_canonical:
            try:
                transformer = get_sentence_transformer()
                cand_skill_list = list(resume_canonical)
                cand_embeddings = transformer.encode(cand_skill_list, convert_to_tensor=True)

                for key in missing_keys:
                    req_name = job_skills_lower[key]
                    req_emb = transformer.encode(req_name, convert_to_tensor=True)
                    cos_scores = util.cos_sim(req_emb, cand_embeddings)[0]
                    best_idx = int(cos_scores.argmax())
                    best_score = float(cos_scores[best_idx])
                    best_cand_skill = cand_skill_list[best_idx]

                    # Threshold for related technical skill equivalence
                    if best_score >= 0.70:
                        partial_credit = round(min(0.85, best_score * 0.85), 2)
                        matched_skills[f"{req_name} (~{best_cand_skill})"] = round(best_score, 2)
                        matched_points += partial_credit
                    else:
                        missing_skills[req_name] = 0.85
            except Exception:
                for key in missing_keys:
                    missing_skills[job_skills_lower[key]] = 0.85
        else:
            for key in missing_keys:
                missing_skills[job_skills_lower[key]] = 0.85

        skill_overlap_score = min(100.0, (matched_points / len(job_skills_lower)) * 100)
    else:
        skill_overlap_score = 50.0

    # Semantic similarity using multi-chunk document embeddings
    try:
        transformer = get_sentence_transformer()
        emb_resume = encode_document(resume_text, transformer)
        emb_job = encode_document(job_text, transformer)
        cosine_sim = float(util.cos_sim(emb_resume, emb_job)[0][0])
        semantic_score = max(0.0, min(100.0, cosine_sim * 100))
    except Exception:
        semantic_score = skill_overlap_score

    # Adaptive Weighting:
    # If a candidate has strong semantic alignment (>65%) but descriptive phrasing caused lower exact skill overlap,
    # balance weights dynamically (50% semantic / 50% skill) instead of penalizing unfairly.
    if semantic_score >= 65.0 and skill_overlap_score < 50.0:
        skill_weight = 0.45
        semantic_weight = 0.55
    else:
        skill_weight = 0.60
        semantic_weight = 0.40

    final_score = round((skill_overlap_score * skill_weight) + (semantic_score * semantic_weight), 1)

    # Generate explanation text
    if final_score >= 80:
        explanation = f"Excellent match ({final_score}%). Strong coverage on core skills."
    elif final_score >= 60:
        explanation = f"Good match ({final_score}%). Matched {len(matched_skills)} skills, missing {len(missing_skills)} key skills."
    else:
        explanation = f"Moderate/Low match ({final_score}%). Consider strengthening missing skills: {', '.join(list(missing_skills.keys())[:3])}."

    return {
        'match_score': final_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'explanation': explanation
    }
