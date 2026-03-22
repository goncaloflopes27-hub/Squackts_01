from __future__ import annotations

import sqlite3

from utils import now_iso


def create(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        INSERT INTO products(id,sku,nome,descricao,preco_cents,custo_cents,stock,stock_minimo,tipo_producao,
        image_path,design_path,ativo,created_at,updated_at)
        VALUES(:id,:sku,:nome,:descricao,:preco_cents,:custo_cents,:stock,:stock_minimo,:tipo_producao,
        :image_path,:design_path,:ativo,:created_at,:updated_at)
        """,
        payload,
    )


def update(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        UPDATE products SET sku=:sku,nome=:nome,descricao=:descricao,preco_cents=:preco_cents,custo_cents=:custo_cents,
        stock=:stock,stock_minimo=:stock_minimo,tipo_producao=:tipo_producao,image_path=:image_path,design_path=:design_path,
        ativo=:ativo,updated_at=:updated_at WHERE id=:id
        """,
        payload,
    )


def list_all(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM products ORDER BY nome COLLATE NOCASE").fetchall()


def get_by_id(conn: sqlite3.Connection, product_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()


def get_by_sku(conn: sqlite3.Connection, sku: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM products WHERE sku=?", (sku,)).fetchone()


def change_stock(conn: sqlite3.Connection, product_id: str, delta: int) -> None:
    conn.execute("UPDATE products SET stock=stock+?, updated_at=? WHERE id=?", (delta, now_iso(), product_id))
