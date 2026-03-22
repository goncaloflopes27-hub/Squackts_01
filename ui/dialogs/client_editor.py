from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class ClientEditorDialog(tk.Toplevel):
    def __init__(self, master, client_service, existing=None):
        super().__init__(master)
        self.client_service = client_service
        self.existing = existing or {}
        self.title("Editor de cliente")
        self.transient(master)
        self.grab_set()
        self.vars = {k: tk.StringVar(value=str(self.existing.get(k, ""))) for k in ["nome", "email", "telefone", "nif", "morada", "notas"]}
        row = 0
        for key in ["nome", "email", "telefone", "nif", "morada", "notas"]:
            ttk.Label(self, text=key).grid(row=row, column=0, sticky="w", padx=6, pady=4)
            ttk.Entry(self, textvariable=self.vars[key], width=48).grid(row=row, column=1, padx=6, pady=4)
            row += 1
        ttk.Button(self, text="Guardar", command=self.save).grid(row=row, column=1, sticky="e", padx=6, pady=8)

    def save(self):
        data = {k: v.get() for k, v in self.vars.items()}
        data.update({"id": self.existing.get("id"), "created_at": self.existing.get("created_at")})
        try:
            self.client_service.save(data)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc), parent=self)
