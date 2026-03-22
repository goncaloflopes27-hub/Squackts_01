from __future__ import annotations

from tkinter import ttk

from ui.dialogs.product_editor import ProductEditorDialog


class ProductsTab(ttk.Frame):
    def __init__(self, master, product_service):
        super().__init__(master)
        self.product_service = product_service
        ttk.Button(self, text="Novo produto", command=self.new_product).pack(anchor="w", padx=8, pady=8)
        self.tree = ttk.Treeview(self, columns=("sku", "nome", "tipo", "stock"), show="headings")
        for c in ("sku", "nome", "tipo", "stock"):
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.edit_selected)
        self.refresh()

    def refresh(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for p in self.product_service.list_all():
            self.tree.insert("", "end", iid=p["id"], values=(p["sku"], p["nome"], p["tipo_producao"], p["stock"]))

    def new_product(self):
        ProductEditorDialog(self, self.product_service)
        self.refresh()

    def edit_selected(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        product = next((x for x in self.product_service.list_all() if x["id"] == sel[0]), None)
        if product:
            ProductEditorDialog(self, self.product_service, existing=dict(product))
            self.refresh()
