from __future__ import annotations

from tkinter import ttk

from config import get_paths


class SystemTab(ttk.Frame):
    page_key = "sistema"

    def __init__(self, master, backup_service, logs_repo, conn):
        super().__init__(master, style="App.TFrame", padding=12)
        self.backup_service = backup_service
        self.logs_repo = logs_repo
        self.conn = conn

        paths = get_paths()
        top = ttk.Frame(self, style="App.TFrame")
        top.pack(fill="x")

        card_paths = ttk.Labelframe(top, text="Caminhos do sistema", style="Card.TLabelframe", padding=10)
        card_paths.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ttk.Label(card_paths, text=f"DB: {paths.db_path}", style="Body.TLabel", wraplength=500).pack(anchor="w")
        ttk.Label(card_paths, text=f"Images: {paths.images_dir}", style="Body.TLabel", wraplength=500).pack(anchor="w")
        ttk.Label(card_paths, text=f"Backups: {paths.backups_dir}", style="Body.TLabel", wraplength=500).pack(anchor="w")

        card_db = ttk.Labelframe(top, text="Backups e manutencao", style="Card.TLabelframe", padding=10)
        card_db.pack(side="left", fill="both", expand=True)
        ttk.Button(card_db, text="Criar backup", command=self.create_backup, style="Primary.TButton").pack(anchor="w")
        self.info = ttk.Label(card_db, text="", style="Muted.TLabel")
        self.info.pack(anchor="w", pady=(6, 0))

        logs_box = ttk.Labelframe(self, text="Historico de atividade", style="Card.TLabelframe", padding=8)
        logs_box.pack(fill="both", expand=True, pady=(10, 0))
        self.logs = ttk.Treeview(logs_box, columns=("timestamp", "entidade", "acao", "detalhe"), show="headings")
        for c, t, w in [
            ("timestamp", "Timestamp", 170),
            ("entidade", "Entidade", 90),
            ("acao", "Acao", 160),
            ("detalhe", "Detalhe", 420),
        ]:
            self.logs.heading(c, text=t)
            self.logs.column(c, width=w)
        self.logs.pack(fill="both", expand=True)
        self.refresh()

    def header(self) -> tuple[str, str]:
        return "Sistema", "Backups, logs e manutencao local"

    def actions(self):
        return [("Criar backup", self.create_backup, "Primary.TButton")]

    def on_search(self, query: str):
        self.refresh(query=query)

    def create_backup(self):
        path = self.backup_service.create_backup()
        self.info.config(text=f"Backup criado em: {path}")
        self.refresh()

    def refresh(self, query: str = ""):
        for iid in self.logs.get_children():
            self.logs.delete(iid)
        for row in self.logs_repo.list_recent(self.conn, 100):
            if query and query.lower() not in (row["acao"] or "").lower() and query.lower() not in (row["detalhe"] or "").lower():
                continue
            self.logs.insert("", "end", values=(row["timestamp"], row["entidade"], row["acao"], row["detalhe"]))
