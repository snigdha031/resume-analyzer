import re

SKILL_LIST = [
    "python", "sql", "pandas", "numpy", "matplotlib",
    "seaborn", "power bi", "tableau", "excel",
    "machine learning", "deep learning", "nlp",
    "google cloud", "gcp", "aws", "azure",
    "docker", "kubernetes", "fastapi",
    "rest api", "git", "data analysis",
    "data visualization", "etl", "data pipelines"
]

def clean_text(text: str):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    return text

def extract_skills(text: str):
    text = clean_text(text)

    found_skills = []

    for skill in SKILL_LIST:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))