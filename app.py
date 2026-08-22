import os
import re

import streamlit as st
from dotenv import load_dotenv

from chains import analyze_career_fit, analyze_jd_match
from credit_store import consume_credit, get_or_create_user, reset_test_credits
from security_utils import safe_html, validate_upload

load_dotenv()

STARTING_CREDITS = 10
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
ACCESS_CODE = os.getenv("TEST_ACCESS_CODE", "").strip()

st.set_page_config(
    page_title="Smart ATS | Resume Match",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1180px; padding-top: 1.6rem; padding-bottom: 4rem;}
      .hero {
        padding: 2rem 2.1rem;
        border: 1px solid rgba(128,128,128,.20);
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(99,102,241,.14), rgba(14,165,233,.07));
        margin-bottom: 1.35rem;
      }
      .hero h1 {margin: 0 0 .5rem 0; font-size: 2.45rem; letter-spacing: -.04em;}
      .hero p {margin: 0; opacity: .78; font-size: 1.06rem; max-width: 790px;}
      .eyebrow {font-size: .80rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: .65; margin-bottom: .5rem;}
      .credit-card {
        border: 1px solid rgba(99,102,241,.32);
        background: rgba(99,102,241,.08);
        border-radius: 16px;
        padding: .9rem 1rem;
        margin: .4rem 0 1rem 0;
      }
      .credit-number {font-size: 1.7rem; font-weight: 800; line-height: 1;}
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
      .decision {
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 16px;
        padding: 1rem 1.15rem;
        margin: .8rem 0 1rem 0;
      }
      div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.18);
        border-radius: 14px;
        padding: .75rem .9rem;
      }
      div[data-testid="stButton"] > button {border-radius: 12px; min-height: 3rem; font-weight: 700;}
      .fineprint {opacity: .6; font-size: .82rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def valid_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value.strip()))


def render_recharge() -> None:
    st.error("You've used all 10 test credits.", icon="🔒")
    st.markdown(
        """
        <div class="price-box">
          <div class="eyebrow">Recharge</div>
          <h3 style="margin:.1rem 0 .35rem 0;">10 more analyses — ₹99</h3>
          <p style="margin:0; opacity:.72;">Payments are intentionally disabled in this test MVP. Production recharge will happen only after server-side payment verification.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def charge_after_success(email: str, result: dict, state_key: str) -> None:
    updated = consume_credit(email)
    st.session_state[state_key] = result
    st.session_state[f"{state_key}_email"] = email
    st.session_state["credits_remaining"] = updated["credits"]
    st.rerun()


def render_chips(values: list[str], prefix: str = "") -> None:
    if not values:
        st.caption("Nothing returned here.")
        return
    chips = "".join(
        f'<span class="chip">{safe_html(prefix + str(item))}</span>'
        for item in values
    )
    st.markdown(chips, unsafe_allow_html=True)


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Resume intelligence for real applications</div>
      <h1>Know where you fit — and what to fix.</h1>
      <p>Compare your resume with a job description, or evaluate your readiness for a target role. The app gives focused, evidence-based guidance without pretending to be an employer's actual ATS.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

api_ready = bool(os.getenv("OPENAI_API_KEY"))

with st.sidebar:
    st.markdown("## 🎯 Smart ATS")
    st.caption("Private MVP test")

    access_granted = True
    if ACCESS_CODE:
        access_input = st.text_input("Tester access code", type="password")
        access_granted = access_input == ACCESS_CODE
        if access_input and not access_granted:
            st.error("Invalid access code.")
        elif access_granted:
            st.success("Tester access unlocked.")

    email = st.text_input(
        "Your email",
        placeholder="you@example.com",
        help="Used only to track MVP credits.",
        disabled=not access_granted,
    ).strip().lower()

    user = None
    if access_granted and email and valid_email(email):
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
                st.caption("Available only while TEST_MODE=true.")
                if st.button("Reset my 10 test credits", use_container_width=True):
                    reset_test_credits(email)
                    for key in list(st.session_state.keys()):
                        if key.startswith("jd_result") or key.startswith("career_result"):
                            st.session_state.pop(key, None)
                    st.rerun()
    elif access_granted and email:
        st.warning("Enter a valid email address.")
    elif access_granted:
        st.info("Enter your email to activate 10 test credits.")

    st.divider()
    st.markdown("**Security by design**")
    st.caption("Model and prompts are server-controlled. No browser tools, web search, API key, or model selector is exposed to users.")

if not api_ready:
    st.warning("Server setup incomplete: OPENAI_API_KEY is not configured.", icon="⚙️")

if user and user["credits"] <= 0:
    render_recharge()

email_ready = bool(access_granted and email and valid_email(email))
credits_ready = bool(user and user["credits"] > 0)
base_ready = api_ready and email_ready and credits_ready

jd_tab, career_tab = st.tabs(["📄 JD vs Resume", "🎯 Career Fit"])

with jd_tab:
    st.markdown("### Should I apply to this job?")
    st.caption("Upload your resume and paste the exact JD. One successful analysis uses one credit.")

    left, right = st.columns([1.08, .92], gap="large")
    with left:
        jd_text = st.text_area(
            "Job description",
            height=330,
            placeholder="Paste the complete job description...",
            max_chars=30_000,
            key="jd_text",
        )
    with right:
        jd_resume = st.file_uploader(
            "Resume PDF",
            type=["pdf"],
            help="Text-based PDF only. Maximum 5 MB and 10 pages.",
            key="jd_resume",
        )
        if jd_resume:
            st.success(f"Ready: {jd_resume.name}")
        st.markdown("**You'll get**")
        st.markdown("• Match score\n\n• Apply / improve / weak-fit decision\n\n• Keyword gaps\n\n• Strengths and risks\n\n• Top 5 fixes")

    run_jd = st.button(
        "Analyze JD Match — 1 Credit",
        type="primary",
        use_container_width=True,
        disabled=not (base_ready and jd_text.strip() and jd_resume),
        key="run_jd",
    )

    if run_jd and jd_resume:
        try:
            validate_upload(jd_resume)
            with st.spinner("Comparing resume with job requirements..."):
                result = analyze_jd_match(jd_resume.getvalue(), jd_text)
            if "error" in result:
                st.error(result["error"])
                st.info("No credit was used because the analysis did not complete.")
            else:
                charge_after_success(email, result, "jd_result")
        except Exception as exc:
            st.error(str(exc))
            st.info("No credit was used.")

    result = st.session_state.get("jd_result")
    if result and st.session_state.get("jd_result_email") == email:
        st.divider()
        st.markdown("## JD Match Report")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Estimated Match", f"{result['match_score']}%")
        m2.metric("Match Level", result["match_level"])
        m3.metric("Matched Keywords", len(result["matched_keywords"]))
        m4.metric("Missing Keywords", len(result["missing_keywords"]))
        st.progress(result["match_score"] / 100)

        decision = safe_html(result["application_decision"])
        reason = safe_html(result["decision_reason"])
        st.markdown(
            f'<div class="decision"><div class="eyebrow">Application decision</div><h3 style="margin:.1rem 0 .35rem 0;">{decision}</h3><p style="margin:0; opacity:.75;">{reason}</p></div>',
            unsafe_allow_html=True,
        )

        overview, keywords, summary, fixes = st.tabs(["Overview", "Keywords", "Summary", "Top Fixes"])
        with overview:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Strengths")
                for item in result["strengths"]:
                    st.success(item)
            with c2:
                st.markdown("#### Gaps / risks")
                for item in result["gaps"]:
                    st.warning(item)
            st.markdown("#### Recruiter-style verdict")
            st.info(result["recruiter_verdict"])
        with keywords:
            st.markdown("#### Matched")
            render_chips(result["matched_keywords"], "✓ ")
            st.markdown("#### Missing / weakly evidenced")
            render_chips(result["missing_keywords"])
        with summary:
            st.info(result["profile_summary"])
            st.caption("Use this only when every statement matches your real experience.")
        with fixes:
            for idx, item in enumerate(result["recommendations"], 1):
                st.markdown(f"**{idx}. {item}**")

with career_tab:
    st.markdown("### How ready am I for my target role?")
    st.caption("Tell us the role you want. The app separates resume-writing gaps from genuine skill gaps. One successful analysis uses one credit.")

    c1, c2 = st.columns([.9, 1.1], gap="large")
    with c1:
        target_role = st.text_input(
            "Target role",
            placeholder="e.g. Generative AI Engineer",
            max_chars=120,
            key="target_role",
        )
        intent = st.text_area(
            "Your intent (optional)",
            placeholder="Example: I want product-focused GenAI roles in the next 3 months. Tell me what I should fix vs genuinely learn.",
            height=180,
            max_chars=2_000,
            key="career_intent",
        )
    with c2:
        career_resume = st.file_uploader(
            "Resume PDF",
            type=["pdf"],
            help="Text-based PDF only. Maximum 5 MB and 10 pages.",
            key="career_resume",
        )
        if career_resume:
            st.success(f"Ready: {career_resume.name}")
        st.markdown("**You'll get**")
        st.markdown("• Role-readiness score\n\n• Current strengths\n\n• Resume visibility gaps\n\n• Genuine skill gaps\n\n• Learning plan\n\n• Similar role families")

    run_career = st.button(
        "Analyze Career Fit — 1 Credit",
        type="primary",
        use_container_width=True,
        disabled=not (base_ready and target_role.strip() and career_resume),
        key="run_career",
    )

    if run_career and career_resume:
        try:
            validate_upload(career_resume)
            with st.spinner("Evaluating role readiness..."):
                result = analyze_career_fit(career_resume.getvalue(), target_role, intent)
            if "error" in result:
                st.error(result["error"])
                st.info("No credit was used because the analysis did not complete.")
            else:
                charge_after_success(email, result, "career_result")
        except Exception as exc:
            st.error(str(exc))
            st.info("No credit was used.")

    result = st.session_state.get("career_result")
    if result and st.session_state.get("career_result_email") == email:
        st.divider()
        st.markdown("## Career Fit Report")

        m1, m2 = st.columns(2)
        m1.metric("Role Readiness", f"{result['readiness_score']}%")
        m2.metric("Readiness Level", result["readiness_level"])
        st.progress(result["readiness_score"] / 100)
        st.info(result["positioning"])

        strengths_tab, gaps_tab, plan_tab, roles_tab = st.tabs(["Strengths", "Gap Diagnosis", "Plan", "Similar Roles"])
        with strengths_tab:
            for item in result["strengths"]:
                st.success(item)
        with gaps_tab:
            st.markdown("#### Resume visibility gaps")
            st.caption("These may be capabilities you have, but your resume does not evidence them clearly enough.")
            for item in result["resume_visibility_gaps"]:
                st.warning(item)
            st.markdown("#### Genuine skill gaps")
            st.caption("The resume does not demonstrate these capabilities. Learn/build them before claiming them.")
            for item in result["skill_gaps"]:
                st.error(item)
        with plan_tab:
            st.markdown("#### Resume fixes")
            for idx, item in enumerate(result["resume_fixes"], 1):
                st.markdown(f"**{idx}. {item}**")
            st.markdown("#### Learning plan")
            for idx, item in enumerate(result["learning_plan"], 1):
                st.markdown(f"**{idx}. {item}**")
            st.markdown("#### Best next step")
            st.info(result["next_step"])
        with roles_tab:
            for role in result["similar_roles"]:
                st.markdown(f"**{safe_html(role['role'])} — {role['fit_score']}%**")
                st.caption(role["why"])

if user:
    current = get_or_create_user(email)
    if current["credits"] <= 0:
        st.markdown("---")
        render_recharge()

st.markdown("---")
st.markdown(
    '<p class="fineprint">Security note: user-provided resume/JD text is treated as untrusted data. The app does not expose the API key, system prompt, model selector, browsing tools, or code execution to users. No prompt-injection defense is perfect, so production should also use authentication, persistent server-side credits, logging, rate limits, and payment verification.</p>',
    unsafe_allow_html=True,
)
