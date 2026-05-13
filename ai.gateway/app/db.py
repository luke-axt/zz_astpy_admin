import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "usage.sqlite"


async def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                user TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                model TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                duration_ms INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON requests(timestamp)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_requests_user ON requests(user)
        """)
        await db.commit()


async def log_request(
    user: str,
    endpoint: str,
    model: str,
    status_code: int,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    duration_ms: int = 0,
):
    import time

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO requests
            (timestamp, user, endpoint, model, status_code, prompt_tokens, completion_tokens, total_tokens, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                time.time(),
                user,
                endpoint,
                model,
                status_code,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                duration_ms,
            ),
        )
        await db.commit()
