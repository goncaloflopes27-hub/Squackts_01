from __future__ import annotations

import sqlite3

from services.order_service import OrderService


class ProductionService:
    def __init__(self, conn: sqlite3.Connection):
        self.order_service = OrderService(conn)
        self.conn = conn

    def queue(self, status: str = "pendente", query: str = ""):

        q = f"%{query.lower()}%"
        return self.conn.execute(
            """
            SELECT o.id as order_id, oi.id as item_id, o.numero, o.estado_producao, o.data_prevista,
                   c.nome as client_nome, oi.nome_snapshot, oi.quantidade, oi.tipo_producao_snapshot
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            LEFT JOIN clients c ON c.id = o.client_id
            WHERE o.estado_producao=?
              AND (?='' OR lower(o.numero) LIKE ? OR lower(COALESCE(c.nome,'')) LIKE ? OR lower(oi.nome_snapshot) LIKE ?)
            ORDER BY COALESCE(o.data_prevista,''), o.created_at ASC
            """,
            (status, query, q, q, q),
        ).fetchall()

    def set_status(self, order_id: str, status: str) -> None:
        self.order_service.update_states_tracking_paid(order_id, estado_producao=status)


    def get_production_queue(self, status: str = "pendente", query: str = ""):
        return self.queue(status=status, query=query)

    def mark_producing(self, order_id: str, item_id: str | None = None) -> None:
        self.set_status(order_id, "em_producao")

    def mark_produced(self, order_id: str, item_id: str | None = None) -> None:
        self.set_status(order_id, "produzida")

    def mark_ready(self, order_id: str, item_id: str | None = None) -> None:
        self.set_status(order_id, "pronta_envio")
