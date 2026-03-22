from __future__ import annotations

import sqlite3


def create_order(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        INSERT INTO orders(id,numero,client_id,estado_comercial,estado_producao,estado_envio,pago,tracking,
        metodo_pagamento,subtotal_cents,portes_cents,total_cents,data_prevista,notas,created_at,updated_at)
        VALUES(:id,:numero,:client_id,:estado_comercial,:estado_producao,:estado_envio,:pago,:tracking,
        :metodo_pagamento,:subtotal_cents,:portes_cents,:total_cents,:data_prevista,:notas,:created_at,:updated_at)
        """,
        payload,
    )


def update_order(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        UPDATE orders SET client_id=:client_id,estado_comercial=:estado_comercial,estado_producao=:estado_producao,
        estado_envio=:estado_envio,pago=:pago,tracking=:tracking,metodo_pagamento=:metodo_pagamento,
        subtotal_cents=:subtotal_cents,portes_cents=:portes_cents,total_cents=:total_cents,data_prevista=:data_prevista,
        notas=:notas,updated_at=:updated_at WHERE id=:id
        """,
        payload,
    )


def list_orders(conn: sqlite3.Connection, query: str = "", estado: str = "todos", pago: str = "todos") -> list[sqlite3.Row]:
    clauses = ["1=1"]
    params: list = []
    if query:
        clauses.append("(lower(o.numero) LIKE ? OR lower(COALESCE(c.nome,'')) LIKE ?)")
        q = f"%{query.lower()}%"
        params.extend([q, q])
    if estado != "todos":
        clauses.append("o.estado_producao = ?")
        params.append(estado)
    if pago == "pago":
        clauses.append("o.pago = 1")
    elif pago == "nao_pago":
        clauses.append("o.pago = 0")

    sql = (
        "SELECT o.*, c.nome as client_nome FROM orders o "
        "LEFT JOIN clients c ON c.id=o.client_id "
        f"WHERE {' AND '.join(clauses)} ORDER BY o.created_at DESC"
    )
    return conn.execute(sql, tuple(params)).fetchall()


def get_order(conn: sqlite3.Connection, order_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()


def delete_items(conn: sqlite3.Connection, order_id: str) -> None:
    conn.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))


def insert_item(conn: sqlite3.Connection, payload: dict) -> None:
    conn.execute(
        """
        INSERT INTO order_items(id,order_id,product_id,sku_snapshot,nome_snapshot,quantidade,preco_unit_cents,
        custo_unit_cents,tipo_producao_snapshot,personalizacao,stock_deducted,stock_returned)
        VALUES(:id,:order_id,:product_id,:sku_snapshot,:nome_snapshot,:quantidade,:preco_unit_cents,
        :custo_unit_cents,:tipo_producao_snapshot,:personalizacao,:stock_deducted,:stock_returned)
        """,
        payload,
    )


def list_items(conn: sqlite3.Connection, order_id: str) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)).fetchall()
