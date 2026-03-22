from __future__ import annotations

from contextlib import contextmanager
import sqlite3

from config import get_paths
from schema import DDL, SCHEMA_VERSION


def connect() -> sqlite3.Connection:
    paths = get_paths()
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(paths.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def init_database() -> None:
    conn = connect()
    try:
        with transaction(conn):
            conn.executescript(DDL)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    finally:
        conn.close()


def backup_database(destination: str) -> None:
    src = connect()
    dst = sqlite3.connect(destination)
    try:
        src.backup(dst)
        dst.commit()
    finally:
        src.close()
        dst.close()
