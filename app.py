import os

import streamlit as st
from dotenv import load_dotenv

from chains import DEFAULT_MODEL, process_resume

load_dotenv()

st.set_page_config(
    page_title="Smart ATS Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
      .hero {
        padding: 1.4rem 1.6rem;
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(99,102,241,.10), rgba(14,165,233,.05));
        margin-bottom: 1.5rem;
      }
      .hero h1 {margin: 0 0 .35rem 0; font-size: 2.15rem;}
      .hero p {margin: 0; opacity: .78; font-size: 1.02rem;}
      .section-card {
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin-bottom: .85rem;
      }
      .chip {
        display: inline-block;
        padding: .28rem .55rem;
        margin: .2rem .22rem .2rem 0;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 999px;
        font-size: .85rem;
      }
      .muted {opacity: .68; font-size: .9rem;}
      div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 14px;
        padding: .7rem .9rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🎯 Smart ATS Resume Analyzer</h1>
      <p>Compare your resume against a job description and get an AI-estimated ATS match, keyword gaps, strengths, recruiter-style feedback, and targeted improvements.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Configuration")
    model = st.text_input("OpenAI model", value=os.getenv("OPENAI_MODEL", DEFAULT_MODEL))
    api_ready = bool(os.getenv("OPENAI_API_KEY"))
    if api_ready:
        st.success("OPENAI_API_KEY detected")
    else:
        st.error("OPENAI_API_KEY not found")
    st.caption("Add your key to a local `.env` file. Never commit the real key to GitHub.")
    st.divider()
    st.subheader("What this checks")
    st.markdown("• Skill and keyword overlap\n\n• Resume/JD alignment\n\n• Missing requirements\n\n• Recruiter-style strengths and gaps\n\n• Tailored summary and next actions")
    st.divider()
    st.caption("The match score is an AI estimate, not a score from a specific ATS vendor.")

left, right = st.columns([1.08, 0.92], gap="large")

with left:
    st.subheader("1. Job Description")
    jd_text = st.text_area(
        "Paste the complete job description",
        height=340,
        placeholder="Paste responsibilities, required skills, preferred qualifications, tools, domain experience, etc.",
        label_visibility="collapsed",
    )
    st.caption(f"{len(jd_text):,} characters")

with right:
    st.subheader("2. Resume PDF")
    uploaded_file = st.file_uploader(
        "Upload a text-based PDF resume",
        type=["pdf"],
        help="Scanned image-only PDFs may not contain extractable text.",
    )

    if uploaded_file:
        size_kb = len(uploaded_file.getvalue()) / 1024
        st.success(f"Loaded: {uploaded_file.name}")
        st.caption(f"PDF size: {size_kb:.1f} KB")
    else:
        st.info("Upload the resume you want to compare against the JD.")

    st.markdown("#### Before analyzing")
    st.markdown(
        "• Use the full JD, not only the title\n\n"
        "• Upload your latest resume version\n\n"
        "• Keep claims truthful—recommendations should improve wording, not invent experience"
    )

analyze = st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True,
    disabled=not (jd_text.strip() and uploaded_file and api_ready),
)

if not api_ready:
    st.warning("Create a `.env` file with `OPENAI_API_KEY=...` before running an analysis.")

if analyze and uploaded_file:
    with st.spinner("Analyzing resume-to-job fit..."):
        response = process_resume(uploaded_file.getvalue(), jd_text, model=model.strip() or DEFAULT_MODEL)

    if "error" in response:
        st.error(response["error"])
    else:
        st.divider()
        st.subheader("Analysis Results")

        score = response.get("match_score", 0)
        matched = response.get("matched_keywords", [])
        missing = response.get("missing_keywords", [])
        strengths = response.get("strengths", [])
        gaps = response.get("gaps", [])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Estimated Match", f"{score}%")
        m2.metric("Match Level", response.get("match_level", "—"))
        m3.metric("Matched Keywords", len(matched))
        m4.metric("Missing Keywords", len(missing))

        st.progress(score / 100)

        tabs = st.tabs(["Overview", "Keywords", "Tailored Summary", "Recommendations"])

        with tabs[0]:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown("#### Strengths")
                if strengths:
                    for item in strengths:
                        st.success(item)
                else:
                    st.caption("No strengths returned.")
            with c2:
                st.markdown("#### Gaps / Risks")
                if gaps:
                    for item in gaps:
                        st.warning(item)
                else:
                    st.caption("No major gaps returned.")

            st.markdown("#### Recruiter Verdict")
            st.info(response.get("recruiter_verdict", "No verdict returned."))

        with tabs[1]:
            st.markdown("#### Matched Keywords")
            if matched:
                st.markdown(
                    "".join(f'<span class="chip">✓ {item}</span>' for item in matched),
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No matched keywords returned.")

            st.markdown("#### Missing Keywords")
            if missing:
                st.markdown(
                    "".join(f'<span class="chip">{item}</span>' for item in missing),
                    unsafe_allow_html=True,
                )
            else:
                st.success("No major missing keywords returned.")

        with tabs[2]:
            st.markdown("#### Tailored Professional Summary")
            st.info(response.get("profile_summary", "No summary returned."))
            st.caption("Use this as a starting point only. Keep every claim consistent with your actual resume and experience.")

        with tabs[3]:
            recommendations = response.get("recommendations", [])
            if recommendations:
                for idx, item in enumerate(recommendations, start=1):
                    st.markdown(f"**{idx}. {item}**")
            else:
                st.caption("No recommendations returned.")

        st.caption(
            "AI-generated analysis can miss context. Use the output as a resume-improvement aid rather than a guarantee of recruiter or ATS outcomes."
        )
