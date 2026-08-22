# 🎯 Smart ATS Resume Analyzer

A Streamlit app that compares a resume PDF against a job description using the OpenAI API. It produces an **AI-estimated ATS match**, matched and missing keywords, strengths, gaps, a tailored summary, recruiter-style feedback, and practical resume recommendations.

> The score is an AI estimate for resume/JD alignment. It is not a score from a specific ATS vendor and does not guarantee interview selection.

## ✨ Features

- Upload a text-based PDF resume
- Paste a complete job description
- OpenAI-powered resume-to-JD analysis
- Estimated match score and match level
- Matched vs. missing keyword breakdown
- Strengths and hiring-screen gaps
- Tailored professional summary
- Prioritized resume recommendations
- Prompt-injection-resistant system instructions
- API key loaded safely from a local `.env` file

## 🧰 Requirements

- Python 3.10+
- An OpenAI API key

## 🚀 Setup

```bash
git clone https://github.com/arpitchalakh/smart-ats-analyzer.git
cd smart-ats-analyzer

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

Create your local environment file:

```bash
cp .env.example .env
```

On Windows PowerShell you can use:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini
```

The real `.env` file is ignored by Git and should never be committed.

## ▶️ Run

```bash
streamlit run app.py
```

Open the local Streamlit URL shown in your terminal, paste a JD, upload a resume PDF, and click **Analyze Resume**.

## 📁 Project Structure

```text
smart-ats-analyzer/
├── app.py              # Streamlit UI
├── chains.py           # PDF extraction + OpenAI analysis
├── requirements.txt    # Python dependencies
├── .env.example        # Safe environment template
├── .gitignore
└── README.md
```

## 🔐 Privacy & Security

Resume and job-description text are sent to the configured OpenAI API model when you click Analyze. Do not upload information you are not comfortable processing through the API.

The app treats content inside the resume and JD as untrusted data so embedded instructions should not override the analyzer's system behavior.

## ⚠️ PDF Notes

This version extracts text directly from PDFs. Image-only or scanned resumes may return no readable text. Export the resume as a normal text-based PDF before analyzing.

## 🛠️ Configuration

You can change the default model in `.env`:

```env
OPENAI_MODEL=gpt-5-mini
```

You can also change the model from the Streamlit sidebar for a session.

## 📌 Recommended Next Improvements

Potential future additions include DOCX support, deterministic keyword scoring alongside the LLM score, downloadable reports, resume version comparison, optional OCR for scanned PDFs, authentication, and automated tests.
