# Jagadeesh Agentic Job Search

Local review-first job agent with optional browser-based Apply Agent.

## Features
- Naukri, LinkedIn and public ATS search links
- Import public job pages or paste job descriptions
- Match jobs to the candidate profile
- Generate a truthful job-tailored CV and application answers
- Export PDF/DOCX
- Application tracker
- **AI Apply Agent:** opens a real Chrome window, fills supported application fields, and leaves the form ready for review
- Optional one-job-at-a-time final submit when explicitly enabled and no CAPTCHA/MFA/login warning is detected

## Setup
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m uvicorn app.server:app --reload
```
Open http://127.0.0.1:8000

## Apply Agent
1. Import/paste one job.
2. Open **Review Application**.
3. Click **Start AI Apply Agent**.
4. A Chrome window opens using a separate local browser profile.
5. Log in manually if the job site asks.
6. In Review mode, the agent fills supported fields but does not submit.
7. For explicit final-submit mode, check the option before starting. The agent will not bypass CAPTCHA/MFA or automatically accept legal/consent checkboxes.

Do not use this for bulk/mass applications. Site terms, employer application rules, and account security controls still apply.
