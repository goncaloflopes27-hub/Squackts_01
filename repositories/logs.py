from __future__ import annotations

import sqlite3


def create_log(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        INSERT INTO logs(id, timestamp, entidade, entidade_id, acao, detalhe, payload_json)
        VALUES(:id, :timestamp, :entidade, :entidade_id, :acao, :detalhe, :payload_json)
        """,
        payload,
    )


def list_recent(conn: sqlite3.Connection, limit: int = 100) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
