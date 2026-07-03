# database.py
# Oddiy SQLite bazasi bilan ishlash uchun funksiyalar

import sqlite3
import json
from datetime import date
from contextlib import contextmanager

DB_PATH = "hisobot.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS operators (
                chat_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                added_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_chat_id INTEGER NOT NULL,
                report_date TEXT NOT NULL,
                answers TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(operator_chat_id, report_date)
            )
        """)


def add_operator(chat_id: int, full_name: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO operators (chat_id, full_name, added_at) VALUES (?, ?, ?)",
            (chat_id, full_name, date.today().isoformat()),
        )


def is_operator(chat_id: int) -> bool:
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM operators WHERE chat_id = ?", (chat_id,)).fetchone()
        return row is not None


def get_all_operators():
    with get_conn() as conn:
        rows = conn.execute("SELECT chat_id, full_name FROM operators").fetchall()
        return [(r["chat_id"], r["full_name"]) for r in rows]


def get_operator_name(chat_id: int) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT full_name FROM operators WHERE chat_id = ?", (chat_id,)).fetchone()
        return row["full_name"] if row else "Noma'lum"


def save_report(operator_chat_id: int, report_date: str, answers: dict):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO reports (operator_chat_id, report_date, answers, created_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(operator_chat_id, report_date)
               DO UPDATE SET answers = excluded.answers, created_at = excluded.created_at""",
            (operator_chat_id, report_date, json.dumps(answers, ensure_ascii=False), date.today().isoformat()),
        )


def get_reports_for_date(report_date: str):
    """Returns list of (operator_chat_id, full_name, answers_dict) for a given date."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.operator_chat_id, o.full_name, r.answers
               FROM reports r
               JOIN operators o ON o.chat_id = r.operator_chat_id
               WHERE r.report_date = ?""",
            (report_date,),
        ).fetchall()
        result = []
        for r in rows:
            result.append((r["operator_chat_id"], r["full_name"], json.loads(r["answers"])))
        return result


def get_reports_for_range(start_date: str, end_date: str):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.operator_chat_id, o.full_name, r.report_date, r.answers
               FROM reports r
               JOIN operators o ON o.chat_id = r.operator_chat_id
               WHERE r.report_date BETWEEN ? AND ?
               ORDER BY r.report_date""",
            (start_date, end_date),
        ).fetchall()
        result = []
        for r in rows:
            result.append((r["operator_chat_id"], r["full_name"], r["report_date"], json.loads(r["answers"])))
        return result
