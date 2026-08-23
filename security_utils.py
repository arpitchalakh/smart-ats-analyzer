import html
import re

MAX_JD_CHARS = 30_000
MAX_TARGET_ROLE_CHARS = 120
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def clean_untrusted_text(value: str, max_chars: int) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid text input.")
    value = CONTROL_CHARS.sub(" ", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.strip()
    if len(value) > max_chars:
        raise ValueError(f"Input is too long. Maximum length is {max_chars:,} characters.")
    return value


def validate_jd(value: str) -> str:
    value = clean_untrusted_text(value, MAX_JD_CHARS)
    if len(value) < 80:
        raise ValueError("Paste a more complete job description before analyzing.")
    return value


def validate_target_role(value: str) -> str:
    value = clean_untrusted_text(value, MAX_TARGET_ROLE_CHARS)
    if len(value) < 2:
        raise ValueError("Enter the role you want to target.")
    return value


def validate_upload(uploaded_file) -> None:
    if uploaded_file is None:
        raise ValueError("Upload a resume PDF.")
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError("Resume PDF is too large. Maximum upload size is 5 MB.")
    if not uploaded_file.name.lower().endswith(".pdf"):
        raise ValueError("Only PDF resumes are supported in this MVP.")


def safe_html(value: str) -> str:
    return html.escape(str(value), quote=True)
