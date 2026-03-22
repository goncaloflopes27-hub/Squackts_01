from __future__ import annotations

from decimal import Decimal
from tkinter import ttk

from ui.dialogs.product_editor import ProductEditorDialog


class ProductsTab(ttk.Frame):
    page_key = "catalogo"

    def __init__(self, master, product_service):
        super().__init__(master, style="App.TFrame", padding=12)
        self.product_service = product_service

        filter_row = ttk.Frame(self, style="App.TFrame")
        filter_row.pack(fill="x", pady=(0, 8))
        self.tipo_var = ttk.Combobox(filter_row, values=["todos", "print_on_demand", "stock_fisico", "misto"], width=20)
        self.tipo_var.set("todos")
        self.tipo_var.pack(side="left", padx=(0, 8))
        ttk.Button(filter_row, text="Filtrar", command=self.refresh, style="Ghost.TButton").pack(side="left")

        pane = ttk.Panedwindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True)

        left = ttk.Labelframe(pane, text="Catalogo de produtos", style="Card.TLabelframe", padding=8)
        right = ttk.Labelframe(pane, text="Resumo do produto", style="Card.TLabelframe", padding=10)
        pane.add(left, weight=4)
        pane.add(right, weight=3)

        self.tree = ttk.Treeview(
            left,
            columns=("nome", "sku", "tipo", "preco", "custo", "margem", "stock", "min", "estado"),
            show="headings",
        )
        for key, title, width in [
            ("nome", "Nome", 180),
            ("sku", "SKU", 110),
            ("tipo", "Tipo", 110),
            ("preco", "Preco", 80),
            ("custo", "Custo", 80),
            ("margem", "Margem", 90),
            ("stock", "Stock", 70),
            ("min", "Min", 60),
            ("estado", "Estado", 80),
        ]:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._update_detail)
        self.tree.bind("<Double-1>", self.edit_selected)

        self.detail = ttk.Label(right, text="Selecione um produto para detalhe.", style="Body.TLabel", justify="left")
        self.detail.pack(fill="x")

        self.refresh()

    def header(self) -> tuple[str, str]:
        return "Catalogo", "Gestao de SKUs, margens e regras de producao"

    def actions(self):
        return [("Novo produto", self.new_product, "Primary.TButton")]

    def on_search(self, query: str):
        self.refresh(query=query)

    def refresh(self, query: str = ""):
        tipo = self.tipo_var.get() if hasattr(self, "tipo_var") else "todos"
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for p in self.product_service.list_all(query=query, tipo=tipo):
            preco = Decimal(p["preco_cents"]) / Decimal(100)
            custo = Decimal(p["custo_cents"]) / Decimal(100)
            margem = preco - custo
            estado = "Ativo" if p["ativo"] else "Inativo"
            self.tree.insert(
                "",
                "end",
                iid=p["id"],
                values=(
                    p["nome"], p["sku"], p["tipo_producao"],
                    f"{preco:.2f}", f"{custo:.2f}", f"{margem:.2f}",
                    p["stock"], p["stock_minimo"], estado,
                ),
            )

    def new_product(self):
        ProductEditorDialog(self, self.product_service)
        self.refresh()

    def edit_selected(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        product = self.product_service.get_by_id(sel[0])
        if product:
            ProductEditorDialog(self, self.product_service, existing=dict(product))
            self.refresh()

    def _update_detail(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            self.detail.config(text="Selecione um produto para detalhe.")
            return
        p = self.product_service.get_by_id(sel[0])
        if not p:
            return
        preco = Decimal(p["preco_cents"]) / Decimal(100)
        custo = Decimal(p["custo_cents"]) / Decimal(100)
        margem = preco - custo
        margem_pct = Decimal("0") if preco == 0 else (margem / preco) * Decimal(100)
        txt = (
            f"{p['nome']} ({p['sku']})\n"
            f"Tipo: {p['tipo_producao']}\n"
            f"Preco/Custo: {preco:.2f} / {custo:.2f} EUR\n"
            f"Margem: {margem:.2f} EUR ({margem_pct:.1f}%)\n"
            f"Stock: {p['stock']} (min {p['stock_minimo']})\n"
            f"Imagem: {p['image_path'] or '-'}\n"
            f"Notas: {p['descricao'] or '-'}"
        )
        self.detail.config(text=txt)
