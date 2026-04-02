# AI-Powered Resume Analyzer

An end-to-end AI application that analyzes and ranks resumes against a job description using a hybrid scoring system — combining rule-based skill matching with Google Gemini semantic analysis.

🔗 **Live Demo:** [resume-analyzer.streamlit.app](snigdha031/resume-analyzer/main/streamlit_app.py) 
🛠 **Backend API:** [resume-analyzer on Render](https://resume-analyzer-236k.onrender.com)

---

## Features

### AI-Powered Scoring
- **Rule-Based Skill Matching** — extracts and compares skills from resume vs job description
- **Semantic Scoring** — uses Google Gemini 2.5 Flash to evaluate contextual relevance beyond keyword matching
- **Hybrid Final Score** — weighted combination of both scoring methods

### Analytics Dashboard
- Score distribution histogram
- Candidate ranking bar chart
- Rule vs Semantic scatter plot
- Score spread boxplot

### Skill Gap Analytics
- Candidate × Skill coverage heatmap (green = present, red = missing)
- Skill supply vs demand gap chart across all candidates
- Top missing skills summary table

### Statistical Analysis
- **Z-Score Normalization** — shows each candidate's standing relative to the pool
- **Percentile Ranking** — ranks candidates as Top 10%, Top 25%, etc.
- **Weighted Scoring Experiment** — interactive slider to adjust Rule vs Semantic weight in real time

### AI Ranking Explanation
- Generates a plain English paragraph explaining why candidates ranked the way they did
- Highlights key skill differences, strengths, and recruiter recommendations

### Export
- Download full results as CSV
- Download filtered results (by minimum score threshold) as CSV

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| AI / LLM | Google Gemini 2.5 Flash (google-genai SDK) |
| PDF Parsing | pdfplumber |
| Data Analysis | Pandas, SciPy |
| Visualization | Plotly Express |
| Deployment (Backend) | Render |
| Deployment (Frontend) | Streamlit Cloud |

---

## Architecture

```
User (Streamlit Cloud)
        │
        │  HTTP POST (PDF + JD text)
        ▼
FastAPI Backend (Render)
        │
        ├── Rule-Based Skill Matching (jd_parser + matcher)
        │
        └── Google Gemini API (semantic scoring + AI insights)
                │
                ▼
        JSON Response → Streamlit UI
        (scores, skills, strengths, weaknesses, summary)
```

---

## Project Structure

```
resume-analyzer/
│
├── app/
│   ├── main.py              # FastAPI routes
│   ├── ai_service.py        # Gemini API integration
│   ├── resume_parser.py     # PDF text extraction
│   ├── jd_parser.py         # Skill extraction from JD
│   └── matcher.py           # Rule-based skill matching
│
├── streamlit_app.py         # Frontend UI
├── requirements.txt         # Dependencies
├── render.yaml              # Render deployment config
├── Procfile                 # Process configuration
├── .gitignore
└── README.md
```

---

## Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/snigdha031/resume-analyzer.git
cd resume-analyzer
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your free API key at [Google AI Studio](https://aistudio.google.com)

### 5. Run the backend
```bash
uvicorn app.main:app --reload
```

### 6. Run the frontend (in a new terminal)
```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser.

---

## How It Works

1. **Upload** one or more resume PDFs
2. **Paste** the job description
3. **Click** Analyze Resumes
4. The backend:
   - Extracts text from each PDF using `pdfplumber`
   - Identifies skills from both resume and JD
   - Calculates rule-based match score
   - Sends resume + JD to Gemini for semantic analysis
   - Returns hybrid score + AI insights
5. The frontend displays:
   - Ranked comparison table
   - Analytics charts
   - Skill gap heatmaps
   - Statistical breakdown
   - AI plain-English explanation

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/full-analysis/` | Analyze a single resume against a JD |
| POST | `/explain-ranking/` | Generate AI explanation for candidate rankings |
| POST | `/analyze-jd/` | Extract skills from a job description |
| POST | `/upload-resume/` | Extract text from a resume PDF |

---

## Deployment

### Backend → Render
- Free tier web service
- Auto-deploys on every GitHub push
- Environment variable: `GEMINI_API_KEY`

### Frontend → Streamlit Cloud
- Free tier
- Auto-deploys on every GitHub push
- Secrets: `GEMINI_API_KEY` (set in Streamlit Cloud dashboard)

---

## Future Improvements
- [ ] Database integration (PostgreSQL) for storing historical analysis runs
- [ ] Support for DOCX resume format
- [ ] Multi-language JD support
- [ ] Interview question generator based on skill gaps
- [ ] Resume scoring trend over time

---

## Author

**Snigdha Raghavan**  
[GitHub](https://github.com/snigdha031) · [LinkedIn](https://www.linkedin.com/in/snigdha-rp-32a03820a/) ← add your LinkedIn

---

## License

MIT License — free to use and modify.
