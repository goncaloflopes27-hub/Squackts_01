from __future__ import annotations

from tkinter import ttk

from config import get_paths


class SystemTab(ttk.Frame):
    def __init__(self, master, backup_service, logs_repo, conn):
        super().__init__(master)
        self.backup_service = backup_service
        self.logs_repo = logs_repo
        self.conn = conn
        paths = get_paths()
        ttk.Label(self, text=f"DB: {paths.db_path}").pack(anchor="w", padx=8, pady=2)
        ttk.Label(self, text=f"Images: {paths.images_dir}").pack(anchor="w", padx=8, pady=2)
        ttk.Label(self, text=f"Backups: {paths.backups_dir}").pack(anchor="w", padx=8, pady=2)
        ttk.Button(self, text="Criar backup", command=self.create_backup).pack(anchor="w", padx=8, pady=8)
        self.logs = ttk.Treeview(self, columns=("timestamp", "acao", "detalhe"), show="headings")
        for c in ("timestamp", "acao", "detalhe"):
            self.logs.heading(c, text=c)
        self.logs.pack(fill="both", expand=True)
        self.refresh()

    def create_backup(self):
        self.backup_service.create_backup()
        self.refresh()

    def refresh(self):
        for iid in self.logs.get_children():
            self.logs.delete(iid)
        for row in self.logs_repo.list_recent(self.conn, 50):
            self.logs.insert("", "end", values=(row["timestamp"], row["acao"], row["detalhe"]))
