import io
from docx import Document
import httpx
from app.config import settings

# ---------------- PDF/DOCX extraction ----------------
def extract_text_from_pdf(data: bytes) -> str:
    import pdfplumber
    with io.BytesIO(data) as f:
        text_all = []
        with pdfplumber.open(f) as pdf:
            for page in pdf.pages:
                text_all.append(page.extract_text() or "")
        return "\n".join(text_all)

def extract_text_from_docx(data: bytes) -> str:
    with io.BytesIO(data) as f:
        doc = Document(f)
        return "\n".join(p.text for p in doc.paragraphs)

# ---------------- Named Entity Recognition (NER) via HF API ----------------
async def extract_job_skills(resume_text: str) -> dict:
    """
    Extract job skills from the resume text using Hugging Face API (NER model).
    Returns extracted skills.
    """
    if not settings.HUGGINGFACE_API_KEY:
        return {"skills": []}

    try:
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
        payload = {"inputs": resume_text[:1000]}  # Pass resume text for NER processing

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english",
                headers=headers,
                json=payload
            )
            data = response.json()

            # Extract the job skills (entities) from the response
            skills = [entity['word'] for entity in data if entity['entity'] == 'B-JobSkill']
            return {"skills": skills}

    except Exception as e:
        print(f"Error during inference: {e}")
        return {"skills": []}

# ---------------- Resume & Job Description Similarity (Optional) ----------------
async def resume_jd_similarity(resume_text: str, job_description: str) -> dict:
    """
    Compute semantic similarity between resume and job description using Hugging Face API.
    Returns similarity score 0-100.
    """
    if not settings.HUGGINGFACE_API_KEY:
        resume_words = set(resume_text.lower().split())
        jd_words = set(job_description.lower().split())
        inter = len(resume_words & jd_words)
        score = round(100 * inter / max(1, len(jd_words)), 2)
        return {"similarity_score": score}

    try:
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
        payload = {
            "inputs": {
                "source_sentence": resume_text[:1000],
                "sentences": [job_description[:1000]]
            }
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/dbmdz/bert-large-cased-finetuned-conll03-english",
                headers=headers,
                json=payload
            )
            data = response.json()
            score = round(float(data[0]["score"]) * 100, 2)
            return {"similarity_score": score}
    except Exception as e:
        # Fallback simple word overlap
        resume_words = set(resume_text.lower().split())
        jd_words = set(job_description.lower().split())
        inter = len(resume_words & jd_words)
        score = round(100 * inter / max(1, len(jd_words)), 2)
        return {"similarity_score": score}
