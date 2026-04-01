def calculate_match(resume_skills: list, jd_skills: list):
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = resume_set.intersection(jd_set)
    missing = jd_set - resume_set

    if len(jd_set) == 0:
        return 0, [], []

    score = (len(matched) / len(jd_set)) * 100

    return round(score, 2), list(matched), list(missing)