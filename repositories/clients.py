from __future__ import annotations

import sqlite3


def create(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        INSERT INTO clients(id,nome,email,telefone,nif,morada,notas,ativo,created_at,updated_at)
        VALUES(:id,:nome,:email,:telefone,:nif,:morada,:notas,:ativo,:created_at,:updated_at)
        """,
        payload,
    )


def update(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        UPDATE clients SET nome=:nome,email=:email,telefone=:telefone,nif=:nif,morada=:morada,
        notas=:notas,ativo=:ativo,updated_at=:updated_at WHERE id=:id
        """,
        payload,
    )


def list_all(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM clients ORDER BY nome COLLATE NOCASE").fetchall()


def get_by_id(conn: sqlite3.Connection, client_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM clients WHERE id=?", (client_id,)).fetchone()
