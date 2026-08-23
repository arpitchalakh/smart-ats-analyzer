import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path("ats_mvp.db")
STARTING_CREDITS = 10


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(_connect()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY COLLATE NOCASE,
                credits INTEGER NOT NULL DEFAULT 10,
                analyses INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_or_create_user(email: str) -> dict:
    email = normalize_email(email)
    if not email:
        raise ValueError("Email is required.")

    with closing(_connect()) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (email, credits) VALUES (?, ?)",
            (email, STARTING_CREDITS),
        )
        conn.commit()
        row = conn.execute(
            "SELECT email, credits, analyses FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    return dict(row)


def consume_credit(email: str) -> dict:
    """Atomically consume one credit. Raises ValueError when none remain."""
    email = normalize_email(email)

    with closing(_connect()) as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT credits, analyses FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT INTO users (email, credits) VALUES (?, ?)",
                (email, STARTING_CREDITS),
            )
            credits = STARTING_CREDITS
            analyses = 0
        else:
            credits = int(row["credits"])
            analyses = int(row["analyses"])

        if credits <= 0:
            conn.rollback()
            raise ValueError("No credits remaining.")

        conn.execute(
            """
            UPDATE users
            SET credits = credits - 1,
                analyses = analyses + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
            """,
            (email,),
        )
        conn.commit()

    return {"email": email, "credits": credits - 1, "analyses": analyses + 1}


def reset_test_credits(email: str) -> dict:
    email = normalize_email(email)
    with closing(_connect()) as conn:
        conn.execute(
            """
            INSERT INTO users (email, credits, analyses)
            VALUES (?, ?, 0)
            ON CONFLICT(email) DO UPDATE SET
                credits = excluded.credits,
                analyses = 0,
                updated_at = CURRENT_TIMESTAMP
            """,
            (email, STARTING_CREDITS),
        )
        conn.commit()
    return get_or_create_user(email)


init_db()
