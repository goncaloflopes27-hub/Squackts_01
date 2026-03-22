from __future__ import annotations

from pathlib import Path
from decimal import Decimal, InvalidOperation
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ProductEditorDialog(tk.Toplevel):
    def __init__(self, master, product_service, existing=None):
        super().__init__(master)
        self.product_service = product_service
        self.existing = existing or {}
        self.image_source: Path | None = None
        self.title("Editor de produto")
        self.transient(master)
        self.grab_set()
        fields = ["sku", "nome", "descricao", "preco", "custo", "stock", "stock_minimo", "design_path"]
        self.vars = {k: tk.StringVar(value=str(self.existing.get(k, self.existing.get(f"{k}_cents", "")))) for k in fields}
        self.vars["preco"].set(str((self.existing.get("preco_cents", 0) or 0) / 100))
        self.vars["custo"].set(str((self.existing.get("custo_cents", 0) or 0) / 100))
        self.tipo = tk.StringVar(value=self.existing.get("tipo_producao", "print_on_demand"))
        row = 0
        for key in fields:
            ttk.Label(self, text=key).grid(row=row, column=0, sticky="w", padx=6, pady=4)
            ttk.Entry(self, textvariable=self.vars[key], width=44).grid(row=row, column=1, padx=6, pady=4)
            row += 1
        ttk.Label(self, text="tipo_producao").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(self, textvariable=self.tipo, values=["print_on_demand", "stock_fisico", "misto"], state="readonly").grid(row=row, column=1, padx=6, pady=4)
        row += 1
        ttk.Button(self, text="Imagem", command=self.pick_image).grid(row=row, column=0, padx=6, pady=4)
        self.margin_label = ttk.Label(self, text="Margem: -")
        self.margin_label.grid(row=row, column=1, sticky="w", padx=6, pady=4)
        row += 1
        ttk.Button(self, text="Guardar", command=self.save).grid(row=row, column=1, sticky="e", padx=6, pady=8)
        self.vars["preco"].trace_add("write", lambda *_: self.update_margin())
        self.vars["custo"].trace_add("write", lambda *_: self.update_margin())
        self.update_margin()

    def pick_image(self):
        f = filedialog.askopenfilename(parent=self, filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp")])
        if f:
            self.image_source = Path(f)

    def update_margin(self):
        try:
            p = Decimal(self.vars["preco"].get() or "0")
            c = Decimal(self.vars["custo"].get() or "0")
            m = p - c
            pct = Decimal("0") if p == 0 else (m / p) * Decimal("100")
            self.margin_label.config(text=f"Margem: {m:.2f} EUR ({pct:.1f}%)")
        except (InvalidOperation, ValueError):
            self.margin_label.config(text="Margem: inválida")

    def save(self):
        data = {k: v.get() for k, v in self.vars.items()}
        data.update({
            "id": self.existing.get("id"),
            "created_at": self.existing.get("created_at"),
            "tipo_producao": self.tipo.get(),
            "image_source": self.image_source,
            "image_path": self.existing.get("image_path", ""),
        })
        try:
            self.product_service.save(data)
            self.destroy()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc), parent=self)
