from __future__ import annotations

from decimal import Decimal
import tkinter as tk
from tkinter import messagebox, ttk


class OrderEditorDialog(tk.Toplevel):
    def __init__(self, master, order_service, client_service, product_service, existing_order=None, existing_items=None):
        super().__init__(master)
        self.order_service = order_service
        self.client_service = client_service
        self.product_service = product_service
        self.existing_order = existing_order
        self.items_buffer: list[dict] = []
        self.title("Encomenda")
        self.transient(master)
        self.grab_set()
        self.geometry("900x680")

        self.clients = list(self.client_service.list_all())
        self.products = list(self.product_service.list_all())

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Detalhe da encomenda", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Dados do cliente, itens, estado e expedicao.", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))

        if not self.clients:
            ttk.Label(root, text="Crie um cliente antes de criar encomendas.", style="Body.TLabel").pack(anchor="w")
            ttk.Button(root, text="Fechar", command=self.destroy, style="Ghost.TButton").pack(anchor="e", pady=(10, 0))
            return

        self.client_var = tk.StringVar(value=self.clients[0]["id"])
        self.portes_var = tk.StringVar(value="0.00")
        self.metodo_var = tk.StringVar(value="")
        self.tracking_var = tk.StringVar(value="")
        self.estado_comercial = tk.StringVar(value="confirmada")
        self.estado_producao = tk.StringVar(value="pendente")
        self.estado_envio = tk.StringVar(value="por_enviar")
        self.pago_var = tk.IntVar(value=0)
        self.notas_var = tk.StringVar(value="")

        g1 = ttk.Labelframe(root, text="Dados gerais", style="Card.TLabelframe", padding=8)
        g1.pack(fill="x", pady=4)
        ttk.Label(g1, text="Cliente", style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Combobox(g1, textvariable=self.client_var, values=[c["id"] for c in self.clients], width=50).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(g1, text="Portes", style="Muted.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Entry(g1, textvariable=self.portes_var, width=12).grid(row=1, column=1, sticky="w")
        g1.columnconfigure(0, weight=1)

        g2 = ttk.Labelframe(root, text="Itens da encomenda", style="Card.TLabelframe", padding=8)
        g2.pack(fill="both", expand=True, pady=4)
        row = ttk.Frame(g2)
        row.pack(fill="x", pady=(0, 6))
        self.product_var = tk.StringVar(value=self.products[0]["id"] if self.products else "")
        self.qtd_var = tk.StringVar(value="1")
        self.pers_var = tk.StringVar(value="")
        ttk.Combobox(row, textvariable=self.product_var, values=[p["id"] for p in self.products], width=45).pack(side="left", padx=3)
        ttk.Entry(row, textvariable=self.qtd_var, width=6).pack(side="left", padx=3)
        ttk.Entry(row, textvariable=self.pers_var, width=25).pack(side="left", padx=3)
        ttk.Button(row, text="Adicionar item", command=self.add_item, style="Ghost.TButton").pack(side="left", padx=3)

        self.tree = ttk.Treeview(g2, columns=("product", "qtd", "personalizacao"), show="headings", height=10)
        self.tree.heading("product", text="Produto")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("personalizacao", text="Personalizacao")
        self.tree.column("product", width=420)
        self.tree.column("qtd", width=60)
        self.tree.column("personalizacao", width=220)
        self.tree.pack(fill="both", expand=True)

        g3 = ttk.Labelframe(root, text="Estado e expedicao", style="Card.TLabelframe", padding=8)
        g3.pack(fill="x", pady=4)
        ttk.Combobox(g3, textvariable=self.estado_comercial, values=["rascunho", "confirmada", "paga", "cancelada"], width=15).pack(side="left", padx=4)
        ttk.Combobox(g3, textvariable=self.estado_producao, values=["pendente", "em_producao", "produzida", "pronta_envio"], width=15).pack(side="left", padx=4)
        ttk.Combobox(g3, textvariable=self.estado_envio, values=["por_enviar", "expedida", "concluida"], width=15).pack(side="left", padx=4)
        ttk.Checkbutton(g3, text="Pago", variable=self.pago_var).pack(side="left", padx=8)
        ttk.Entry(g3, textvariable=self.metodo_var, width=20).pack(side="left", padx=4)
        ttk.Entry(g3, textvariable=self.tracking_var, width=24).pack(side="left", padx=4)

        g4 = ttk.Labelframe(root, text="Notas e resumo financeiro", style="Card.TLabelframe", padding=8)
        g4.pack(fill="x", pady=4)
        ttk.Entry(g4, textvariable=self.notas_var).pack(fill="x", pady=(0, 6))
        self.resume = ttk.Label(g4, text="Subtotal: 0.00 EUR | Total: 0.00 EUR", style="Body.TLabel")
        self.resume.pack(anchor="w")

        footer = ttk.Frame(root)
        footer.pack(fill="x", pady=(8, 0))
        ttk.Button(footer, text="Cancelar", command=self.destroy, style="Ghost.TButton").pack(side="right", padx=4)
        ttk.Button(footer, text="Guardar", command=self.save, style="Primary.TButton").pack(side="right", padx=4)

        if existing_order and existing_items:
            self.client_var.set(existing_order["client_id"])
            self.portes_var.set(f"{Decimal(existing_order['portes_cents']) / Decimal(100):.2f}")
            self.metodo_var.set(existing_order["metodo_pagamento"] or "")
            self.tracking_var.set(existing_order["tracking"] or "")
            self.estado_comercial.set(existing_order["estado_comercial"])
            self.estado_producao.set(existing_order["estado_producao"])
            self.estado_envio.set(existing_order["estado_envio"])
            self.pago_var.set(int(existing_order["pago"]))
            self.notas_var.set(existing_order["notas"] or "")
            for it in existing_items:
                self.items_buffer.append({"product_id": it["product_id"], "quantidade": it["quantidade"], "personalizacao": it["personalizacao"]})
            self.refresh_items()

        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self.save())

    def add_item(self):
        if not self.product_var.get():
            return
        self.items_buffer.append(
            {
                "product_id": self.product_var.get(),
                "quantidade": int(self.qtd_var.get() or "1"),
                "personalizacao": self.pers_var.get().strip(),
            }
        )
        self.pers_var.set("")
        self.refresh_items()

    def refresh_items(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        subtotal = Decimal("0")
        for idx, item in enumerate(self.items_buffer):
            prod = self.product_service.get_by_id(item["product_id"])
            name = prod["nome"] if prod else item["product_id"]
            if prod:
                subtotal += (Decimal(prod["preco_cents"]) / Decimal(100)) * Decimal(item["quantidade"])
            self.tree.insert("", "end", iid=str(idx), values=(name, item["quantidade"], item["personalizacao"]))
        total = subtotal + Decimal(self.portes_var.get() or "0")
        self.resume.config(text=f"Subtotal: {subtotal:.2f} EUR | Total: {total:.2f} EUR")

    def save(self):
        data = {
            "client_id": self.client_var.get(),
            "portes": self.portes_var.get(),
            "metodo_pagamento": self.metodo_var.get(),
            "tracking": self.tracking_var.get(),
            "estado_comercial": self.estado_comercial.get(),
            "estado_producao": self.estado_producao.get(),
            "estado_envio": self.estado_envio.get(),
            "pago": self.pago_var.get(),
            "notas": self.notas_var.get(),
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
