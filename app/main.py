from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.resume_parser import extract_text_from_pdf
from app.jd_parser import extract_skills
from app.matcher import calculate_match
from app.ai_service import analyze_with_ai, explain_ranking

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Resume Analyzer Running"}


@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    contents = await file.read()
    with open("temp_resume.pdf", "wb") as f:
        f.write(contents)
    text = extract_text_from_pdf("temp_resume.pdf")
    return {
        "filename": file.filename,
        "extracted_text_preview": text[:1000]
    }


@app.post("/analyze-jd/")
def analyze_job_description(jd_text: str = Form(...)):
    skills = extract_skills(jd_text)
    return {
        "total_skills_detected": len(skills),
        "skills": skills
    }


@app.post("/full-analysis/")
async def full_analysis(
    file: UploadFile = File(...),
    jd_text: str = Form(...)
):
    try:
        contents = await file.read()
        with open("temp_resume.pdf", "wb") as f:
            f.write(contents)

        resume_text = extract_text_from_pdf("temp_resume.pdf")

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)
        rule_score, matched_skills, missing_skills = calculate_match(resume_skills, jd_skills)

        ai_result = analyze_with_ai(resume_text, jd_text)

        if isinstance(ai_result, dict) and "semantic_match_score" in ai_result:
            ai_score = ai_result["semantic_match_score"]
        else:
            ai_score = 0

        final_score = round((0.5 * rule_score) + (0.5 * ai_score), 2)

        return {
            "rule_based_score": rule_score,
            "semantic_score": ai_score,
            "final_hybrid_score": final_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "ai_strengths": ai_result.get("strengths", []) if isinstance(ai_result, dict) else [],
            "ai_weaknesses": ai_result.get("weaknesses", []) if isinstance(ai_result, dict) else [],
            "improvement_suggestions": ai_result.get("improvement_suggestions", []) if isinstance(ai_result, dict) else [],
            "tailored_summary": ai_result.get("tailored_summary", "") if isinstance(ai_result, dict) else ""
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/ai-analysis/")
async def ai_analysis(
    file: UploadFile = File(...),
    jd_text: str = Form(...)
):
    try:
        contents = await file.read()
        with open("temp_resume.pdf", "wb") as f:
            f.write(contents)
        resume_text = extract_text_from_pdf("temp_resume.pdf")
        ai_result = analyze_with_ai(resume_text, jd_text)
        return ai_result
    except Exception as e:
        return {"error": str(e)}


# ✅ NEW: Explain Ranking Endpoint
class CandidateSummary(BaseModel):
    name: str
    final_score: float
    rule_score: float
    semantic_score: float
    matched_skills: str
    missing_skills: str
    percentile: float

class ExplainRequest(BaseModel):
    candidates: List[CandidateSummary]

@app.post("/explain-ranking/")
def explain_ranking_endpoint(request: ExplainRequest):
    try:
        explanation = explain_ranking(request.candidates)
        return {"explanation": explanation}
    except Exception as e:
        return {"error": str(e)}