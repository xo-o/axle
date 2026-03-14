import libsql
import os

_internal_db = None


def get_db():
    global _internal_db
    if _internal_db is not None:
        return _internal_db

    url = os.environ.get("TURSO_DATABASE_URL")
    auth_token = os.environ.get("TURSO_AUTH_TOKEN")

    if not url or not auth_token:
        raise ValueError("TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set")

    _internal_db = libsql.connect(database=url, auth_token=auth_token)
    return _internal_db


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS storyboards (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            data TEXT,
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    db.commit()
