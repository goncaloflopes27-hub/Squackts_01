from __future__ import annotations

import sqlite3

from config import get_paths
from db import transaction
from repositories import logs as logs_repo, products as products_repo
from services import ValidationError
from utils import copy_image_with_thumbnail, new_id, now_iso, to_cents, write_json_text


class ProductService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def list_all(self):
        return products_repo.list_all(self.conn)

    def save(self, data: dict) -> str:
        sku = data.get("sku", "").strip()
        if not sku:
            raise ValidationError("SKU é obrigatório.")
        existing = products_repo.get_by_sku(self.conn, sku)
        if existing and existing["id"] != data.get("id"):
            raise ValidationError("SKU já existe.")
        tipo = data.get("tipo_producao", "")
        if tipo not in {"print_on_demand", "stock_fisico", "misto"}:
            raise ValidationError("Tipo de produção inválido.")
        now = now_iso()
        image_path = data.get("image_path", "")
        if data.get("image_source"):
            image_path = str(copy_image_with_thumbnail(data["image_source"], get_paths().images_dir))
        payload = {
            "id": data.get("id") or new_id(),
            "sku": sku,
            "nome": data.get("nome", "").strip(),
            "descricao": data.get("descricao", "").strip(),
            "preco_cents": to_cents(data.get("preco", "0")),
            "custo_cents": to_cents(data.get("custo", "0")),
            "stock": int(data.get("stock", 0)),
            "stock_minimo": int(data.get("stock_minimo", 0)),
            "tipo_producao": tipo,
            "image_path": image_path,
            "design_path": data.get("design_path", ""),
            "ativo": int(data.get("ativo", 1)),
            "created_at": data.get("created_at", now),
            "updated_at": now,
        }
        if payload["nome"] == "":
            raise ValidationError("Nome do produto é obrigatório.")
        if payload["stock"] < 0 or payload["stock_minimo"] < 0:
            raise ValidationError("Stock inválido.")
        is_new = not data.get("id")
        with transaction(self.conn):
            if is_new:
                products_repo.create(self.conn, payload)
            else:
                products_repo.update(self.conn, payload)
            logs_repo.create_log(
                self.conn,
                {
                    "id": new_id(),
                    "timestamp": now,
                    "entidade": "produto",
                    "entidade_id": payload["id"],
                    "acao": "criar" if is_new else "editar",
                    "detalhe": payload["sku"],
                    "payload_json": write_json_text(payload),
                },
            )
        return payload["id"]
