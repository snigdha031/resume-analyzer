import os
import json
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)


def analyze_with_ai(resume_text: str, jd_text: str):
    prompt = f"""
    You are an ATS resume evaluator.

    Compare the resume and job description.

    Return strictly in JSON format with no markdown, no explanation, just raw JSON:

    {{
        "semantic_match_score": number (0-100),
        "strengths": ["string", "string"],
        "weaknesses": ["string", "string"],
        "improvement_suggestions": ["string", "string"],
        "tailored_summary": "string"
    }}

    Resume:
    {resume_text[:2000]}

    Job Description:
    {jd_text}
    """

    raw_text = ""

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0  #makes responses more consistent
            }
        )

        raw_text = response.text.strip()
        cleaned_text = re.sub(r"```json|```", "", raw_text).strip()
        parsed_json = json.loads(cleaned_text)
        return parsed_json

    except json.JSONDecodeError as e:
        print("JSON PARSE ERROR:", e)
        return {"error": "Failed to parse Gemini response", "raw_response": raw_text}

    except Exception as e:
        print("GEMINI API ERROR:", str(e))
        return {"error": f"Gemini API Error: {str(e)}"}


def explain_ranking(candidates: list) -> str:
    """
    Takes a list of candidate summaries and returns a plain English
    explanation of why they ranked the way they did.
    """

    # Build a readable summary for Gemini
    candidate_text = ""
    for i, c in enumerate(candidates):
        candidate_text += f"""
Rank #{i+1}: {c.name}
- Final Score: {c.final_score} (Percentile: {c.percentile}%)
- Rule-Based Score: {c.rule_score} | Semantic Score: {c.semantic_score}
- Matched Skills: {c.matched_skills if c.matched_skills else "None"}
- Missing Skills: {c.missing_skills if c.missing_skills else "None"}
"""

    prompt = f"""
You are an expert HR analyst and recruiter.

Below are the results of an AI-powered resume analysis. Candidates have been ranked by their overall match score against a job description.

{candidate_text}

Write a clear, professional, plain English explanation (4-8 sentences) that covers:
1. Why the top candidate ranked highest — what specific strengths gave them the edge
2. Key differences between candidates — what separates the top from the bottom
3. Which missing skills hurt the lower-ranked candidates the most
4. One actionable recommendation for the recruiter (e.g. who to shortlist, what to look for in interviews)

Write in a confident, human tone. Do NOT use bullet points. Write in flowing paragraphs.
Do NOT mention scores or numbers — focus on skills, strengths and weaknesses instead.
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()

    except Exception as e:
        print("EXPLAIN RANKING ERROR:", str(e))
        return f"Could not generate explanation: {str(e)}"
