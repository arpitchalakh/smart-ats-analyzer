# 🎯 Smart ATS — Secure Two-Tab MVP

A minimal Streamlit MVP with two focused workflows:

1. **JD vs Resume** — compare a resume against a specific job description.
2. **Career Fit** — evaluate readiness for a target role and separate resume-writing gaps from genuine skill gaps.

The app uses a **server-controlled OpenAI model**, gives each test email **10 credits**, consumes one credit only after a successful analysis, and shows a planned **₹99 / 10 analyses** recharge state after credits reach zero.

> Scores are AI-assisted estimates for resume/job alignment. They are not scores from LinkedIn, Naukri, Workday, or any employer ATS and do not guarantee an interview.

## MVP features

### JD vs Resume
- estimated match score
- Apply Now / Improve First / Weak Fit decision
- matched and missing keywords
- strengths and hiring risks
- recruiter-style verdict
- tailored summary
- top 5 fixes

### Career Fit
- readiness score for a target role
- current strengths
- resume visibility gaps
- genuine skill gaps
- resume fixes
- short learning plan
- similar role families
- best next step

### Credits
- 10 test credits per email
- 1 successful report = 1 credit
- failed API/PDF analysis = 0 credits charged
- recharge message at zero credits
- test reset control when `TEST_MODE=true`

## Security / guardrails

The MVP intentionally keeps user control narrow.

- model is selected only on the server
- no model selector in the UI
- system/developer instructions are never editable by users
- resume, JD, target role and career intent are explicitly treated as **untrusted data**
- structured JSON Schema output is required from the model
- no browsing, tools, code execution or external connectors are enabled in model calls
- API key remains server-side in environment variables
- PDF size, page count and text lengths are bounded
- rendered keyword chips are HTML-escaped
- optional private `TEST_ACCESS_CODE` can gate the MVP
- credits are deducted only after a valid structured result is returned

Prompt-injection defenses reduce risk but cannot provide a mathematical guarantee. A paid production release should also add real authentication, persistent server-side credit storage, rate limiting, audit/error logging and verified payment webhooks.

## Model

Default:

```env
OPENAI_MODEL=gpt-5.6-luna
OPENAI_REASONING_EFFORT=low
```

The model is never shown as a selectable option to users. Change it only through deployment configuration after benchmarking representative resume/JD pairs.

## Setup

Requires Python 3.10+ and an OpenAI API key with API billing enabled.

```bash
git clone https://github.com/arpitchalakh/smart-ats-analyzer.git
cd smart-ats-analyzer
git checkout feat/secure-two-tab-mvp

python -m venv .venv
```

Activate the virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.6-luna
OPENAI_REASONING_EFFORT=low
TEST_MODE=true
TEST_ACCESS_CODE=choose-a-private-test-code
```

Never commit the real `.env` file.

## Run

```bash
streamlit run app.py
```

Open the local Streamlit URL, enter the tester access code if configured, enter an email, and use either tab.

## Project structure

```text
smart-ats-analyzer/
├── app.py              # Two-tab Streamlit UI + credit flow
├── chains.py           # Fixed-model OpenAI analysis + strict schemas
├── security_utils.py   # Input bounds, validation and escaping
├── credit_store.py     # SQLite test credits
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Important before accepting ₹99 payments

The current SQLite credit ledger is intentionally for MVP testing only. Do **not** use it as the source of truth for paid credits on ephemeral hosting.

Before production payments, replace it with something like Supabase/Postgres and add:

- authenticated users / magic-link login
- persistent server-side credit ledger
- Razorpay order creation + server-side signature/webhook verification
- idempotent recharge transactions
- request rate limits and abuse controls
- privacy policy, retention/deletion flow and consent copy
- analytics, exception monitoring and API-cost tracking

## Privacy

The app sends resume/JD/target-role text to the configured OpenAI API model only when the user explicitly runs an analysis. The SQLite MVP database stores email, credits and analysis count; it does not intentionally store resume or JD contents.

## Current limitations

- PDF only
- scanned/image-only PDFs are not OCR'd
- no live LinkedIn/Naukri job access
- no payment gateway yet
- no production authentication yet
