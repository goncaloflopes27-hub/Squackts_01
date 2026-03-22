from __future__ import annotations

import sqlite3

from db import transaction
from repositories import clients as clients_repo, logs as logs_repo
from services import ValidationError
from utils import new_id, now_iso, validate_email, validate_nif, write_json_text


class ClientService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def list_all(self, query: str = ""):
        rows = clients_repo.list_all(self.conn)
        q = query.lower().strip()
        if not q:
            return rows
        return [r for r in rows if q in r["nome"].lower() or q in (r["email"] or "").lower() or q in (r["nif"] or "")]

    def get_by_id(self, client_id: str):
        return clients_repo.get_by_id(self.conn, client_id)


    def create_client(self, **data) -> str:
        return self.save(data)

    def update_client(self, client_id: str, **data) -> str:
        data["id"] = client_id
        return self.save(data)

    def list_clients(self, filters: dict | None = None):
        filters = filters or {}
        return self.list_all(query=filters.get("query", ""))
    def save(self, data: dict) -> str:
        if not data.get("nome"):
            raise ValidationError("Nome do cliente é obrigatório.")
        if not validate_email(data.get("email", "")):
            raise ValidationError("Email inválido.")
        if not validate_nif(data.get("nif", "")):
            raise ValidationError("NIF deve ter 9 dígitos.")

        is_new = not data.get("id")
        now = now_iso()
        payload = {
            "id": data.get("id") or new_id(),
            "nome": data["nome"].strip(),
            "email": data.get("email", "").strip(),
            "telefone": data.get("telefone", "").strip(),
            "nif": data.get("nif", "").strip(),
            "morada": data.get("morada", "").strip(),
            "notas": data.get("notas", "").strip(),
            "ativo": int(data.get("ativo", 1)),
            "created_at": data.get("created_at", now),
            "updated_at": now,
        }
        with transaction(self.conn):
            if is_new:
                clients_repo.create(self.conn, payload)
            else:
                clients_repo.update(self.conn, payload)
            logs_repo.create_log(
                self.conn,
                {
                    "id": new_id(),
                    "timestamp": now,
                    "entidade": "cliente",
                    "entidade_id": payload["id"],
                    "acao": "criar" if is_new else "editar",
                    "detalhe": f"Cliente {payload['nome']}",
                    "payload_json": write_json_text(payload),
                },
            )
        return payload["id"]
