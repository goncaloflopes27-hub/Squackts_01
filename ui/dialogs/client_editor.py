from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class ClientEditorDialog(tk.Toplevel):
    def __init__(self, master, client_service, existing=None):
        super().__init__(master)
        self.client_service = client_service
        self.existing = existing or {}
        self.title("Cliente")
        self.transient(master)
        self.grab_set()
        self.geometry("640x460")

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Dados do cliente", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Atualize contactos e dados fiscais.", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))

        self.vars = {k: tk.StringVar(value=str(self.existing.get(k, ""))) for k in ["nome", "email", "telefone", "nif", "morada", "notas"]}

        frm1 = ttk.Labelframe(root, text="Dados principais", style="Card.TLabelframe", padding=8)
        frm1.pack(fill="x", pady=4)
        self._field(frm1, "Nome", self.vars["nome"]).grid(row=0, column=0, sticky="ew", padx=4, pady=4)

        frm2 = ttk.Labelframe(root, text="Contactos", style="Card.TLabelframe", padding=8)
        frm2.pack(fill="x", pady=4)
        self._field(frm2, "Email", self.vars["email"]).grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        self._field(frm2, "Telefone", self.vars["telefone"]).grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        frm2.columnconfigure(0, weight=1)
        frm2.columnconfigure(1, weight=1)

        frm3 = ttk.Labelframe(root, text="Fiscal e morada", style="Card.TLabelframe", padding=8)
        frm3.pack(fill="x", pady=4)
        self._field(frm3, "NIF", self.vars["nif"]).grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        self._field(frm3, "Morada", self.vars["morada"]).grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        frm3.columnconfigure(0, weight=1)
        frm3.columnconfigure(1, weight=1)

        frm4 = ttk.Labelframe(root, text="Notas", style="Card.TLabelframe", padding=8)
        frm4.pack(fill="both", expand=True, pady=4)
        ttk.Entry(frm4, textvariable=self.vars["notas"]).pack(fill="x")

        footer = ttk.Frame(root)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Button(footer, text="Cancelar", command=self.destroy, style="Ghost.TButton").pack(side="right", padx=4)
        ttk.Button(footer, text="Guardar", command=self.save, style="Primary.TButton").pack(side="right", padx=4)

        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self.save())

    def _field(self, parent, label: str, var: tk.StringVar):
        wrap = ttk.Frame(parent)
        ttk.Label(wrap, text=label, style="Muted.TLabel").pack(anchor="w")
        ttk.Entry(wrap, textvariable=var).pack(fill="x")
        return wrap

    def save(self):
        data = {k: v.get() for k, v in self.vars.items()}
        data.update({"id": self.existing.get("id"), "created_at": self.existing.get("created_at")})
        try:
            self.client_service.save(data)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc), parent=self)
