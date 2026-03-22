from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class OrderEditorDialog(tk.Toplevel):
    def __init__(self, master, order_service, client_service, product_service, existing_order=None, existing_items=None):
        super().__init__(master)
        self.order_service = order_service
        self.client_service = client_service
        self.product_service = product_service
        self.existing_order = existing_order
        self.items_buffer = []
        self.title("Editor de encomenda")
        self.transient(master)
        self.grab_set()

        self.clients = list(self.client_service.list_all())
        self.products = list(self.product_service.list_all())
        if not self.clients:
            ttk.Label(self, text="Crie um cliente antes de criar encomendas.").pack(padx=10, pady=10)
            return

        self.client_var = tk.StringVar(value=self.clients[0]["id"])
        self.portes_var = tk.StringVar(value="0")
        self.notas_var = tk.StringVar(value="")
        self.metodo_var = tk.StringVar(value="")
        self.tracking_var = tk.StringVar(value="")

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=6, pady=6)
        ttk.Label(bar, text="Cliente").pack(side="left")
        ttk.Combobox(bar, textvariable=self.client_var, values=[c["id"] for c in self.clients], width=40).pack(side="left", padx=6)
        ttk.Label(bar, text="Portes").pack(side="left")
        ttk.Entry(bar, textvariable=self.portes_var, width=8).pack(side="left", padx=6)

        item_frame = ttk.Frame(self)
        item_frame.pack(fill="x", padx=6, pady=6)
        self.product_var = tk.StringVar(value=self.products[0]["id"] if self.products else "")
        self.qtd_var = tk.StringVar(value="1")
        ttk.Combobox(item_frame, textvariable=self.product_var, values=[p["id"] for p in self.products], width=42).pack(side="left", padx=4)
        ttk.Entry(item_frame, textvariable=self.qtd_var, width=6).pack(side="left", padx=4)
        ttk.Button(item_frame, text="Adicionar", command=self.add_item).pack(side="left", padx=4)

        self.tree = ttk.Treeview(self, columns=("product_id", "quantidade"), show="headings", height=8)
        self.tree.heading("product_id", text="Produto")
        self.tree.heading("quantidade", text="Qtd")
        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=6, pady=6)
        ttk.Label(footer, text="Método").pack(side="left")
        ttk.Entry(footer, textvariable=self.metodo_var, width=20).pack(side="left", padx=4)
        ttk.Label(footer, text="Tracking").pack(side="left")
        ttk.Entry(footer, textvariable=self.tracking_var, width=20).pack(side="left", padx=4)
        ttk.Button(footer, text="Guardar", command=self.save).pack(side="right")

        if existing_order and existing_items:
            self.client_var.set(existing_order["client_id"])
            self.portes_var.set(str(existing_order["portes_cents"] / 100))
            self.metodo_var.set(existing_order["metodo_pagamento"] or "")
            self.tracking_var.set(existing_order["tracking"] or "")
            for it in existing_items:
                self.items_buffer.append({"product_id": it["product_id"], "quantidade": it["quantidade"], "personalizacao": it["personalizacao"]})
            self.refresh_items()

    def add_item(self):
        if not self.product_var.get():
            return
        self.items_buffer.append({"product_id": self.product_var.get(), "quantidade": int(self.qtd_var.get() or "1"), "personalizacao": ""})
        self.refresh_items()

    def refresh_items(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for idx, item in enumerate(self.items_buffer):
            self.tree.insert("", "end", iid=str(idx), values=(item["product_id"], item["quantidade"]))

    def save(self):
        data = {
            "client_id": self.client_var.get(),
            "portes": self.portes_var.get(),
            "metodo_pagamento": self.metodo_var.get(),
            "tracking": self.tracking_var.get(),
            "items": self.items_buffer,
        }
        try:
            if self.existing_order:
                self.order_service.edit(self.existing_order["id"], data)
            else:
                self.order_service.create(data)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc), parent=self)
