from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import sqlite3


class DashboardService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def kpis(self) -> dict:
        today = datetime.now(timezone.utc).date().isoformat()
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        scalar = lambda sql, p=(): self.conn.execute(sql, p).fetchone()[0]

        faturado_cents = scalar("SELECT COALESCE(SUM(total_cents),0) FROM orders WHERE substr(created_at,1,7)=? AND estado_comercial<>'cancelada'", (month,))
        open_count = scalar("SELECT COUNT(*) FROM orders WHERE estado_comercial<>'cancelada'")
        return {
            "encomendas_hoje": scalar("SELECT COUNT(*) FROM orders WHERE substr(created_at,1,10)=?", (today,)),
            "por_pagar": scalar("SELECT COUNT(*) FROM orders WHERE pago=0 AND estado_comercial<>'cancelada'"),
            "pagas_por_produzir": scalar("SELECT COUNT(*) FROM orders WHERE pago=1 AND estado_producao='pendente'"),
            "em_producao": scalar("SELECT COUNT(*) FROM orders WHERE estado_producao='em_producao'"),
            "prontas_envio": scalar("SELECT COUNT(*) FROM orders WHERE estado_producao='pronta_envio'"),
            "atrasadas": scalar("SELECT COUNT(*) FROM orders WHERE data_prevista<>'' AND data_prevista<? AND estado_envio<>'concluida'", (today,)),
            "faturado_mes": f"{Decimal(faturado_cents) / Decimal(100):.2f} EUR",
            "ticket_medio": f"{(Decimal(faturado_cents) / Decimal(max(open_count, 1)) / Decimal(100)):.2f} EUR",
            "stock_baixo": scalar("SELECT COUNT(*) FROM products WHERE stock<=stock_minimo"),
            "sem_tracking": scalar("SELECT COUNT(*) FROM orders WHERE (tracking IS NULL OR tracking='') AND estado_envio<>'concluida'"),
            "pendentes": scalar("SELECT COUNT(*) FROM orders WHERE estado_producao='pendente'"),
        }

    def recent_orders(self, limit: int = 10, query: str = ""):
        q = f"%{query.lower()}%"
        return self.conn.execute(
            """
            SELECT o.* FROM orders o
            LEFT JOIN clients c ON c.id = o.client_id
            WHERE (?='' OR lower(o.numero) LIKE ? OR lower(COALESCE(c.nome,'')) LIKE ?)
            ORDER BY o.created_at DESC LIMIT ?
            """,
            (query, q, q, limit),
        ).fetchall()


    def get_kpis(self) -> dict:
        kpis = self.kpis()
        alerts = [
            {"tipo": "stock_baixo", "valor": kpis["stock_baixo"]},
            {"tipo": "sem_tracking", "valor": kpis["sem_tracking"]},
            {"tipo": "pendentes", "valor": kpis["pendentes"]},
        ]
        recent_orders = [dict(r) for r in self.recent_orders(10)]
        return {"kpis": kpis, "alerts": alerts, "recent_orders": recent_orders}
