from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import sqlite3

from db import transaction
from repositories import logs as logs_repo, orders as orders_repo, products as products_repo, settings as settings_repo
from services import ValidationError
from utils import new_id, now_iso, to_cents, write_json_text


class OrderService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def list_all(self, query: str = "", estado: str = "todos", pago: str = "todos"):
        return orders_repo.list_orders(self.conn, query=query, estado=estado, pago=pago)

    def _next_number(self) -> str:
        year = datetime.utcnow().year
        key = f"seq_order_{year}"
        seq = int(settings_repo.get_value(self.conn, key) or "0") + 1
        settings_repo.set_value(self.conn, key, str(seq))
        return f"ENC-{year}-{seq:04d}"

    def _build_items(self, order_id: str, items: list[dict]) -> tuple[list[dict], int]:
        if not items:
            raise ValidationError("Encomenda deve ter pelo menos um item.")
        subtotal = 0
        out = []
        for item in items:
            product = products_repo.get_by_id(self.conn, item["product_id"])
            if not product:
                raise ValidationError("Produto inválido no item.")
            qtd = int(item["quantidade"])
            if qtd <= 0:
                raise ValidationError("Quantidade deve ser maior que zero.")
            deducted = 0
            tipo = product["tipo_producao"]
            if tipo == "stock_fisico":
                if product["stock"] < qtd:
                    raise ValidationError(f"Stock insuficiente para {product['sku']}")
                products_repo.change_stock(self.conn, product["id"], -qtd)
                deducted = 1
            elif tipo == "misto":
                if product["stock"] >= qtd:
                    products_repo.change_stock(self.conn, product["id"], -qtd)
                    deducted = 1
            unit = int(product["preco_cents"])
            subtotal += unit * qtd
            out.append(
                {
                    "id": new_id(),
                    "order_id": order_id,
                    "product_id": product["id"],
                    "sku_snapshot": product["sku"],
                    "nome_snapshot": product["nome"],
                    "quantidade": qtd,
                    "preco_unit_cents": unit,
                    "custo_unit_cents": int(product["custo_cents"]),
                    "tipo_producao_snapshot": tipo,
                    "personalizacao": item.get("personalizacao", ""),
                    "stock_deducted": deducted,
                    "stock_returned": 0,
                }
            )
        return out, subtotal

    def create(self, data: dict) -> str:
        now = now_iso()
        with transaction(self.conn):
            order_id = new_id()
            numero = self._next_number()
            rows, subtotal = self._build_items(order_id, data["items"])
            portes = to_cents(data.get("portes", "0"))
            payload = {
                "id": order_id,
                "numero": numero,
                "client_id": data["client_id"],
                "estado_comercial": data.get("estado_comercial", "confirmada"),
                "estado_producao": data.get("estado_producao", "pendente"),
                "estado_envio": data.get("estado_envio", "por_enviar"),
                "pago": int(data.get("pago", 0)),
                "tracking": data.get("tracking", ""),
                "metodo_pagamento": data.get("metodo_pagamento", ""),
                "subtotal_cents": subtotal,
                "portes_cents": portes,
                "total_cents": subtotal + portes,
                "data_prevista": data.get("data_prevista", ""),
                "notas": data.get("notas", ""),
                "created_at": now,
                "updated_at": now,
            }
            orders_repo.create_order(self.conn, payload)
            for row in rows:
                orders_repo.insert_item(self.conn, row)
            logs_repo.create_log(self.conn, {
                "id": new_id(), "timestamp": now, "entidade": "encomenda", "entidade_id": order_id,
                "acao": "criar", "detalhe": numero, "payload_json": write_json_text(payload)
            })
            return order_id


    def list_by_client(self, client_id: str, limit: int = 5):
        return self.conn.execute("SELECT * FROM orders WHERE client_id=? ORDER BY created_at DESC LIMIT ?", (client_id, limit)).fetchall()
    def get_with_items(self, order_id: str):
        return orders_repo.get_order(self.conn, order_id), orders_repo.list_items(self.conn, order_id)


    def edit(self, order_id: str, data: dict) -> None:
        now = now_iso()
        with transaction(self.conn):
            order = orders_repo.get_order(self.conn, order_id)
            if not order:
                raise ValidationError("Encomenda não encontrada.")
            old_items = orders_repo.list_items(self.conn, order_id)
            for item in old_items:
                if item["stock_deducted"] == 1 and item["stock_returned"] == 0:
                    products_repo.change_stock(self.conn, item["product_id"], int(item["quantidade"]))
                    self.conn.execute("UPDATE order_items SET stock_returned=1 WHERE id=?", (item["id"],))
            orders_repo.delete_items(self.conn, order_id)
            new_items, subtotal = self._build_items(order_id, data["items"])
            for row in new_items:
                orders_repo.insert_item(self.conn, row)
            payload = dict(order)
            payload.update({
                "client_id": data.get("client_id", order["client_id"]),
                "tracking": data.get("tracking", order["tracking"]),
                "metodo_pagamento": data.get("metodo_pagamento", order["metodo_pagamento"]),
                "notas": data.get("notas", order["notas"]),
                "portes_cents": to_cents(data.get("portes", str((Decimal(order["portes_cents"]) / Decimal(100)).quantize(Decimal("0.01"))))),
                "subtotal_cents": subtotal,
                "total_cents": subtotal + to_cents(data.get("portes", str((Decimal(order["portes_cents"]) / Decimal(100)).quantize(Decimal("0.01"))))),
                "updated_at": now,
            })
            orders_repo.update_order(self.conn, payload)
            logs_repo.create_log(self.conn, {
                "id": new_id(), "timestamp": now, "entidade": "encomenda", "entidade_id": order_id,
                "acao": "editar", "detalhe": order["numero"], "payload_json": write_json_text(payload)
            })
    def cancel(self, order_id: str) -> None:
        now = now_iso()
        with transaction(self.conn):
            order = orders_repo.get_order(self.conn, order_id)
            if not order:
                raise ValidationError("Encomenda não encontrada.")
            items = orders_repo.list_items(self.conn, order_id)
            for item in items:
                if item["stock_deducted"] == 1 and item["stock_returned"] == 0:
                    products_repo.change_stock(self.conn, item["product_id"], int(item["quantidade"]))
                    self.conn.execute("UPDATE order_items SET stock_returned=1 WHERE id=?", (item["id"],))
            update = dict(order)
            update["estado_comercial"] = "cancelada"
            update["updated_at"] = now
            orders_repo.update_order(self.conn, update)
            logs_repo.create_log(self.conn, {
                "id": new_id(), "timestamp": now, "entidade": "encomenda", "entidade_id": order_id,
                "acao": "cancelar", "detalhe": order["numero"], "payload_json": write_json_text({"order_id": order_id})
            })

    def duplicate(self, order_id: str) -> str:
        order, items = self.get_with_items(order_id)
        if not order:
            raise ValidationError("Encomenda não encontrada.")
        payload = {
            "client_id": order["client_id"],
            "portes": str((Decimal(order["portes_cents"]) / Decimal(100)).quantize(Decimal("0.01"))),
            "metodo_pagamento": order["metodo_pagamento"],
            "notas": order["notas"],
            "items": [{"product_id": i["product_id"], "quantidade": i["quantidade"], "personalizacao": i["personalizacao"]} for i in items],
        }
        new_id_value = self.create(payload)
        logs_repo.create_log(self.conn, {
            "id": new_id(), "timestamp": now_iso(), "entidade": "encomenda", "entidade_id": new_id_value,
            "acao": "duplicar", "detalhe": order["numero"], "payload_json": write_json_text({"source": order_id, "new": new_id_value})
        })
        return new_id_value

    def update_states_tracking_paid(self, order_id: str, **fields) -> None:
        now = now_iso()
        with transaction(self.conn):
            order = orders_repo.get_order(self.conn, order_id)
            if not order:
                raise ValidationError("Encomenda não encontrada.")
            payload = dict(order)
            payload.update(fields)
            payload["updated_at"] = now
            orders_repo.update_order(self.conn, payload)
            logs_repo.create_log(self.conn, {
                "id": new_id(), "timestamp": now, "entidade": "encomenda", "entidade_id": order_id,
                "acao": "update_states_tracking_paid", "detalhe": order["numero"], "payload_json": write_json_text(fields)
            })

    def create_order(self, client_id: str, items: list[dict], **extra) -> str:
        payload = {"client_id": client_id, "items": items}
        payload.update(extra)
        return self.create(payload)

    def update_order(self, order_id: str, **data) -> None:
        self.edit(order_id, data)

    def cancel_order(self, order_id: str) -> None:
        self.cancel(order_id)

    def duplicate_order(self, order_id: str) -> str:
        return self.duplicate(order_id)

    def set_paid(self, order_id: str, paid: bool) -> None:
        self.update_states_tracking_paid(order_id, pago=int(bool(paid)))

    def update_tracking(self, order_id: str, tracking: str) -> None:
        self.update_states_tracking_paid(order_id, tracking=tracking)

    def update_states(self, order_id: str, novo_estado: str) -> None:
        self.update_states_tracking_paid(order_id, estado_producao=novo_estado)

    def get_order_detail(self, order_id: str):
        return self.get_with_items(order_id)

    def list_orders(self, filters: dict | None = None):
        filters = filters or {}
        return self.list_all(
            query=filters.get("query", ""),
            estado=filters.get("estado", "todos"),
            pago=filters.get("pago", "todos"),
        )
