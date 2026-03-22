from __future__ import annotations

import sqlite3

from services.order_service import OrderService


class ProductionService:
    def __init__(self, conn: sqlite3.Connection):
        self.order_service = OrderService(conn)
        self.conn = conn

    def queue(self):
        return self.conn.execute(
            "SELECT * FROM orders WHERE estado_producao IN ('pendente','em_producao') ORDER BY created_at ASC"
        ).fetchall()

    def set_status(self, order_id: str, status: str) -> None:
        self.order_service.update_states_tracking_paid(order_id, estado_producao=status)
