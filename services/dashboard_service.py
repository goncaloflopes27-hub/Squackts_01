from __future__ import annotations

import sqlite3


class DashboardService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def kpis(self) -> dict:
        pending = self.conn.execute("SELECT COUNT(*) FROM orders WHERE estado_producao='pendente'").fetchone()[0]
        open_orders = self.conn.execute("SELECT COUNT(*) FROM orders WHERE estado_comercial<>'cancelada'").fetchone()[0]
        low_stock = self.conn.execute("SELECT COUNT(*) FROM products WHERE stock<=stock_minimo").fetchone()[0]
        return {"pendentes": pending, "encomendas_abertas": open_orders, "stock_baixo": low_stock}

    def recent_orders(self, limit: int = 10):
        return self.conn.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
