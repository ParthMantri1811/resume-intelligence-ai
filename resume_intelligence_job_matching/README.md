# CareerLens AI — Resume Intelligence and Job Matching System

A lightweight Streamlit application for resume parsing, explainable job matching and document-grounded retrieval (RAG-style Q&A).

## Features
- Upload PDF, DOCX or TXT resumes.
- Extract text, detect skills and contact details.
- Resume improvement suggestions.
- Add multiple job descriptions and compare roles.
- Explainable match score: 65% skill coverage + 35% TF-IDF text similarity.
- Matched/missing skills, recommendations, chart and CSV report.
- RAG-style Q&A: chunk documents, retrieve relevant passages and show source evidence.
- No paid API key, GPU, database server or external LLM required.

## Run locally
```bash
python -m venv .venv
# Windows Git Bash:
source .venv/Scripts/activate
# Windows CMD:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Free deployment: Streamlit Community Cloud
1. Create a GitHub repository and upload all files in this folder.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Create an app, select your repository and branch.
4. Set the main file path to `app.py`, then deploy.
5. No secrets or API keys are required.

Free hosting resources and availability are subject to current platform limits. Treat uploaded files/session state as temporary; do not rely on this app for permanent storage.

## Test
Use `data/sample_jobs/data_analyst.txt` or `data/sample_jobs/python_developer.txt` as sample job descriptions.

## Limitations
- Skill extraction uses a curated dictionary and can miss synonyms or unlisted skills.
- Scores are heuristic similarity indicators, not probabilities of getting hired.
- Text-based PDFs are supported; scanned PDFs require OCR first.
- The Q&A module retrieves and displays evidence passages rather than generating an LLM-written answer. This keeps it free, deterministic and grounded.
- This is a prototype and should not be used to make automated hiring decisions. Avoid protected or sensitive personal attributes.

## Structure
```text
resume_intelligence_job_matching/
├── app.py
├── requirements.txt
├── README.md
├── Dockerfile
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── analysis.py
│   ├── parsers.py
│   └── rag.py
└── data/sample_jobs/
    ├── data_analyst.txt
    └── python_developer.txt
```
