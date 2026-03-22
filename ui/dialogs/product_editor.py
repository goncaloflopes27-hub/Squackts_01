from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ProductEditorDialog(tk.Toplevel):
    def __init__(self, master, product_service, existing=None):
        super().__init__(master)
        self.product_service = product_service
        self.existing = existing or {}
        self.image_source: Path | None = None
        self.title("Produto")
        self.transient(master)
        self.grab_set()
        self.geometry("760x620")

        self.vars = {k: tk.StringVar(value=str(self.existing.get(k, ""))) for k in ["sku", "nome", "descricao", "stock", "stock_minimo", "design_path"]}
        self.vars["preco"] = tk.StringVar(value=f"{Decimal(self.existing.get('preco_cents', 0)) / Decimal(100):.2f}")
        self.vars["custo"] = tk.StringVar(value=f"{Decimal(self.existing.get('custo_cents', 0)) / Decimal(100):.2f}")
        self.tipo = tk.StringVar(value=self.existing.get("tipo_producao", "print_on_demand"))

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Catalogo - produto", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="Defina identificacao comercial, margem e regras de producao.", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))

        grid = ttk.Frame(root)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        ident = ttk.Labelframe(grid, text="Identificacao", style="Card.TLabelframe", padding=8)
        ident.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)
        self._field(ident, "Nome", self.vars["nome"]).pack(fill="x", pady=3)
        self._field(ident, "SKU", self.vars["sku"]).pack(fill="x", pady=3)
        self._field(ident, "Notas", self.vars["descricao"]).pack(fill="x", pady=3)

        money = ttk.Labelframe(grid, text="Precos e custos", style="Card.TLabelframe", padding=8)
        money.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)
        self._field(money, "Preco (EUR)", self.vars["preco"]).pack(fill="x", pady=3)
        self._field(money, "Custo (EUR)", self.vars["custo"]).pack(fill="x", pady=3)
        self.margin_label = ttk.Label(money, text="Margem: -", style="Body.TLabel")
        self.margin_label.pack(anchor="w", pady=(6, 0))

        stock = ttk.Labelframe(grid, text="Stock", style="Card.TLabelframe", padding=8)
        stock.grid(row=1, column=0, sticky="nsew", padx=(0, 6), pady=4)
        self._field(stock, "Stock atual", self.vars["stock"]).pack(fill="x", pady=3)
        self._field(stock, "Stock minimo", self.vars["stock_minimo"]).pack(fill="x", pady=3)

        prod = ttk.Labelframe(grid, text="Producao", style="Card.TLabelframe", padding=8)
        prod.grid(row=1, column=1, sticky="nsew", padx=(6, 0), pady=4)
        ttk.Label(prod, text="Tipo de producao", style="Muted.TLabel").pack(anchor="w")
        ttk.Combobox(prod, textvariable=self.tipo, values=["print_on_demand", "stock_fisico", "misto"], state="readonly").pack(fill="x", pady=(0, 6))
        self._field(prod, "Design path", self.vars["design_path"]).pack(fill="x", pady=3)

        media = ttk.Labelframe(root, text="Imagem", style="Card.TLabelframe", padding=8)
        media.pack(fill="x", pady=6)
        ttk.Button(media, text="Escolher imagem", command=self.pick_image, style="Ghost.TButton").pack(side="left")
        self.image_label = ttk.Label(media, text=self.existing.get("image_path", "Sem imagem"), style="Muted.TLabel")
        self.image_label.pack(side="left", padx=8)

        footer = ttk.Frame(root)
        footer.pack(fill="x", pady=(8, 0))
        ttk.Button(footer, text="Cancelar", command=self.destroy, style="Ghost.TButton").pack(side="right", padx=4)
        ttk.Button(footer, text="Guardar", command=self.save, style="Primary.TButton").pack(side="right", padx=4)

        self.vars["preco"].trace_add("write", lambda *_: self.update_margin())
        self.vars["custo"].trace_add("write", lambda *_: self.update_margin())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self.save())
        self.update_margin()

    def _field(self, parent, label: str, var: tk.StringVar):
        wrap = ttk.Frame(parent)
        ttk.Label(wrap, text=label, style="Muted.TLabel").pack(anchor="w")
        ttk.Entry(wrap, textvariable=var).pack(fill="x")
        return wrap

    def pick_image(self):
        f = filedialog.askopenfilename(parent=self, filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp")])
        if f:
            self.image_source = Path(f)
            self.image_label.config(text=str(self.image_source))

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
