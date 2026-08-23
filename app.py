import os
import re

import streamlit as st
from dotenv import load_dotenv

from chains import process_resume
from credit_store import consume_credit, get_or_create_user, reset_test_credits

load_dotenv()

STARTING_CREDITS = 10
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"

st.set_page_config(
    page_title="Smart ATS | Resume Match",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1180px; padding-top: 1.7rem; padding-bottom: 4rem;}
      .hero {
        padding: 2rem 2.1rem;
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(99,102,241,.14), rgba(14,165,233,.07));
        margin-bottom: 1.5rem;
      }
      .hero h1 {margin: 0 0 .55rem 0; font-size: 2.55rem; letter-spacing: -.04em;}
      .hero p {margin: 0; opacity: .78; font-size: 1.08rem; max-width: 760px;}
      .eyebrow {font-size: .82rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: .65; margin-bottom: .55rem;}
      .credit-card {
        border: 1px solid rgba(99,102,241,.32);
        background: rgba(99,102,241,.08);
        border-radius: 16px;
        padding: .9rem 1rem;
        margin: .4rem 0 1rem 0;
      }
      .credit-number {font-size: 1.75rem; font-weight: 800; line-height: 1;}
      .credit-label {opacity: .68; font-size: .83rem; margin-top: .25rem;}
      .chip {
        display: inline-block;
        padding: .32rem .62rem;
        margin: .2rem .22rem .2rem 0;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 999px;
        font-size: .85rem;
      }
      .price-box {
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        margin-top: 1rem;
      }
      div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 14px;
        padding: .75rem .9rem;
      }
      div[data-testid="stButton"] > button {border-radius: 12px; min-height: 3rem; font-weight: 700;}
      div[data-testid="stFileUploader"] {border-radius: 14px;}
      .fineprint {opacity: .6; font-size: .82rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def valid_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value.strip()))


def render_recharge() -> None:
    st.error("You've used all 10 resume-match credits.", icon="🔒")
    st.markdown(
        """
        <div class="price-box">
          <div class="eyebrow">Recharge</div>
          <h3 style="margin:.1rem 0 .35rem 0;">10 more job-match analyses — ₹99</h3>
          <p style="margin:0; opacity:.72;">Payment is not connected in this test MVP yet. The production version will recharge credits automatically after payment.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Resume ↔ Job Match</div>
      <h1>Know what's missing before you apply.</h1>
      <p>Upload your resume, paste the job description, and get an AI-assisted match report with keyword gaps, strengths, recruiter-style feedback, and the highest-impact changes to make before applying.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

api_ready = bool(os.getenv("OPENAI_API_KEY"))

with st.sidebar:
    st.markdown("## 🎯 Smart ATS")
    st.caption("MVP test access")

    email = st.text_input(
        "Your email",
        placeholder="you@example.com",
        help="Used only to track your test credits in this MVP.",
    ).strip().lower()

    user = None
    if email and valid_email(email):
        user = get_or_create_user(email)
        credits = user["credits"]
        st.markdown(
            f"""
            <div class="credit-card">
              <div class="credit-number">{credits}/{STARTING_CREDITS}</div>
              <div class="credit-label">analyses remaining</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(credits / STARTING_CREDITS)
        st.caption(f"{user['analyses']} successful analyses used")

        if TEST_MODE:
            with st.expander("Tester controls"):
                st.caption("Visible only while TEST_MODE=true.")
                if st.button("Reset my 10 test credits", use_container_width=True):
                    reset_test_credits(email)
                    st.session_state.pop("analysis_result", None)
                    st.rerun()
    elif email:
        st.warning("Enter a valid email address.")
    else:
        st.info("Enter your email to activate 10 test credits.")

    st.divider()
    st.markdown("**Each report checks**")
    st.markdown(
        "• Resume ↔ JD alignment\n\n"
        "• Matched & missing keywords\n\n"
        "• Strengths & hiring risks\n\n"
        "• Tailored profile summary\n\n"
        "• Prioritized improvements"
    )
    st.divider()
    st.caption("One credit is charged only after a successful analysis. The AI match score is an estimate, not a score from a specific ATS vendor.")

if not api_ready:
    st.warning("Server setup incomplete: OPENAI_API_KEY is not configured.", icon="⚙️")

if user and user["credits"] <= 0:
    render_recharge()

st.markdown("### Match a resume to a job")
input_left, input_right = st.columns([1.08, .92], gap="large")

with input_left:
    st.markdown("#### 1. Paste the job description")
    jd_text = st.text_area(
        "Job description",
        height=330,
        placeholder="Paste the complete JD here — responsibilities, required skills, preferred qualifications, tools, experience requirements, etc.",
        label_visibility="collapsed",
        max_chars=100_000,
    )
    st.caption(f"{len(jd_text):,} characters")

with input_right:
    st.markdown("#### 2. Upload your resume")
    uploaded_file = st.file_uploader(
        "Resume PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Use a text-based PDF. Scanned/image-only PDFs are not supported in this MVP.",
    )

    if uploaded_file:
        size_kb = len(uploaded_file.getvalue()) / 1024
        st.success(f"Ready: {uploaded_file.name}")
        st.caption(f"{size_kb:.1f} KB · PDF")
    else:
        st.info("Drop your latest resume PDF here.")

    st.markdown("##### Better results")
    st.markdown(
        "• Paste the full JD, not only the role title\n\n"
        "• Use your most recent resume\n\n"
        "• Recommendations never intentionally invent experience"
    )

email_ready = bool(email and valid_email(email))
credits_ready = bool(user and user["credits"] > 0)
inputs_ready = bool(jd_text.strip() and uploaded_file)

analyze = st.button(
    "🎯 Analyze Resume — 1 Credit",
    type="primary",
    use_container_width=True,
    disabled=not (api_ready and email_ready and credits_ready and inputs_ready),
)

if email_ready and not credits_ready:
    st.caption("Recharge is required before another analysis can run.")
elif email_ready and credits_ready and not inputs_ready:
    st.caption("Paste a job description and upload a resume to continue.")

if analyze and uploaded_file and user:
    with st.spinner("Comparing your resume with this job..."):
        response = process_resume(uploaded_file.getvalue(), jd_text)

    if "error" in response:
        st.error(response["error"])
        st.info("No credit was used because the analysis did not complete.")
    else:
        try:
            updated_user = consume_credit(email)
        except ValueError:
            st.session_state.pop("analysis_result", None)
            st.rerun()
        else:
            st.session_state["analysis_result"] = response
            st.session_state["analysis_email"] = email
            st.session_state["credits_remaining"] = updated_user["credits"]
            st.rerun()

response = st.session_state.get("analysis_result")
result_email = st.session_state.get("analysis_email")

if response and result_email == email:
    st.divider()
    credits_remaining = st.session_state.get("credits_remaining")
    if credits_remaining is not None:
        st.success(f"Analysis complete · {credits_remaining} credit{'s' if credits_remaining != 1 else ''} remaining")

    st.markdown("## Your Match Report")

    score = int(response.get("match_score", 0))
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

    tabs = st.tabs(["Overview", "Keywords", "Tailored Summary", "Action Plan"])

    with tabs[0]:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("#### What already works")
            if strengths:
                for item in strengths:
                    st.success(item)
            else:
                st.caption("No specific strengths returned.")
        with c2:
            st.markdown("#### Gaps to address")
            if gaps:
                for item in gaps:
                    st.warning(item)
            else:
                st.caption("No major gaps returned.")

        st.markdown("#### Recruiter-style verdict")
        st.info(response.get("recruiter_verdict", "No verdict returned."))

    with tabs[1]:
        st.markdown("#### Matched job keywords")
        if matched:
            st.markdown(
                "".join(f'<span class="chip">✓ {item}</span>' for item in matched),
                unsafe_allow_html=True,
            )
        else:
            st.caption("No matched keywords returned.")

        st.markdown("#### Missing / weakly evidenced keywords")
        if missing:
            st.markdown(
                "".join(f'<span class="chip">{item}</span>' for item in missing),
                unsafe_allow_html=True,
            )
        else:
            st.success("No major missing keywords returned.")

    with tabs[2]:
        st.markdown("#### Tailored professional summary")
        st.info(response.get("profile_summary", "No summary returned."))
        st.caption("Use this as a draft only. Keep every claim consistent with your actual experience.")

    with tabs[3]:
        recommendations = response.get("recommendations", [])
        if recommendations:
            for idx, item in enumerate(recommendations, start=1):
                st.markdown(f"**{idx}. {item}**")
        else:
            st.caption("No recommendations returned.")

    current_user = get_or_create_user(email)
    if current_user["credits"] <= 0:
        st.markdown("---")
        render_recharge()

    st.markdown(
        '<p class="fineprint">AI-generated analysis can miss context. This report is a resume-improvement aid and does not guarantee ATS ranking, recruiter selection, or an interview.</p>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown("### Why job-specific matching matters")
benefit1, benefit2, benefit3 = st.columns(3)
with benefit1:
    st.markdown("**🎯 One JD at a time**")
    st.caption("A strong resume for one role may still miss the language and requirements of another.")
with benefit2:
    st.markdown("**🔍 See the gaps**")
    st.caption("Find important skills and keywords that are absent or not clearly evidenced before applying.")
with benefit3:
    st.markdown("**⚡ Act before you apply**")
    st.caption("Use a prioritized action plan instead of blindly rewriting the entire resume.")
