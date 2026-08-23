# 🎯 Smart ATS Resume Analyzer — MVP v1

A Streamlit MVP that compares a resume PDF against a job description using a fixed OpenAI model. It returns an **AI-estimated ATS match**, matched and missing keywords, strengths, gaps, a tailored summary, recruiter-style feedback, and prioritized improvements.

This MVP includes a simple **10-credit test flow** so you can validate whether users understand and value the product before adding payments and production authentication.

> The score is an AI estimate for resume/JD alignment. It is not a score from a specific ATS vendor and does not guarantee interview selection.

## What is in MVP v1

- Fixed OpenAI model controlled by the server
- Users cannot select or change the model
- Default model: `gpt-5.6-luna`
- 10 test credits per email
- 1 credit charged only after a successful analysis
- Failed API/PDF analyses do not consume credits
- Recharge message after all 10 credits are used
- Test-only credit reset while `TEST_MODE=true`
- Resume PDF upload
- Job-description input
- Estimated match score and match level
- Matched vs. missing keyword breakdown
- Strengths and hiring-screen gaps
- Tailored professional summary
- Prioritized action plan
- Prompt-injection-resistant analysis instructions
- API key loaded from `.env`

## Why GPT-5.6 Luna for the MVP

The ATS workflow is structured extraction, comparison, classification and short-form feedback. `gpt-5.6-luna` is the cost-sensitive GPT-5.6 tier and supports structured outputs, making it a sensible model to benchmark first.

Do not expose the model selector to users. If later testing shows Luna misses important nuance, benchmark the same resume/JD set against `gpt-5.6-terra` before changing production.

## Requirements

- Python 3.10+
- OpenAI API key with API billing enabled

## Setup

```bash
git clone https://github.com/arpitchalakh/smart-ats-analyzer.git
cd smart-ats-analyzer

git checkout feat/mvp-v1-credits
python -m venv .venv
```

Activate the environment:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from the template:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.6-luna
TEST_MODE=true
```

Never commit the real `.env` file.

## Run

```bash
streamlit run app.py
```

Then:

1. Enter an email address.
2. The email automatically receives 10 test credits.
3. Paste a complete job description.
4. Upload a text-based PDF resume.
5. Click **Analyze Resume — 1 Credit**.
6. A credit is consumed only when the analysis succeeds.
7. At zero credits, the app shows the planned **10 more analyses — ₹99** recharge offer.

## Project structure

```text
smart-ats-analyzer/
├── app.py              # Product UI and credit flow
├── chains.py           # PDF extraction + fixed OpenAI analysis
├── credit_store.py     # Lightweight SQLite MVP credits
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Important: test credits are not production billing

`credit_store.py` currently uses local SQLite. That is intentionally lightweight for product testing.

For a real paid deployment, replace it with a persistent database such as Supabase/Postgres and add proper authentication. Local Streamlit/ephemeral hosting storage can reset during redeploys or instance replacement, so it must not be the source of truth for paid credits.

Before collecting real ₹99 payments, add:

- authenticated users / magic-link login
- persistent credits in Postgres/Supabase
- Razorpay payment + verified webhook
- server-side credit recharge after verified payment
- rate limiting / abuse protection
- privacy policy and deletion flow
- basic analytics and error monitoring

## Test mode

While:

```env
TEST_MODE=true
```

a **Reset my 10 test credits** control appears in the sidebar.

For any public production deployment:

```env
TEST_MODE=false
```

## Privacy

Resume and job-description text are sent to the configured OpenAI API model when the user runs an analysis. The MVP does not intentionally store the uploaded resume or JD in the SQLite credit database.

The analyzer treats content inside both documents as untrusted data so embedded instructions should not override the system behavior.

## PDF limitation

MVP v1 extracts embedded PDF text. Scanned/image-only PDFs are not OCR'd yet.

## Suggested validation before adding more features

Test with real applicants and measure:

- analysis completion rate
- useful / not useful feedback
- how many users consume more than one credit
- how many reach the recharge screen
- willingness to pay ₹99 for another 10 analyses
- common missing features requested by users

Only after that validation should the MVP expand into DOCX support, deterministic ATS subscores, downloadable reports, resume rewriting, history, human review, or recruiter workflows.
