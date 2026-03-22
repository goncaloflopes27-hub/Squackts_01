from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3

from config import get_paths
from db import backup_database, transaction
from repositories import logs as logs_repo
from utils import new_id, now_iso, write_json_text


class BackupService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_backup(self) -> Path:
        paths = get_paths()
        paths.backups_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        target = paths.backups_dir / f"squackts_enterprise_backup_{stamp}.db"
        backup_database(str(target))
        with transaction(self.conn):
            logs_repo.create_log(self.conn, {
                "id": new_id(), "timestamp": now_iso(), "entidade": "sistema", "entidade_id": None,
                "acao": "criar_backup", "detalhe": str(target), "payload_json": write_json_text({"backup": str(target)})
            })
        return target
