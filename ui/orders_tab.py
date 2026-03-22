from __future__ import annotations

from tkinter import messagebox, ttk

from ui.dialogs.order_editor import OrderEditorDialog


class OrdersTab(ttk.Frame):
    def __init__(self, master, order_service, client_service, product_service):
        super().__init__(master)
        self.order_service = order_service
        self.client_service = client_service
        self.product_service = product_service
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=6)
        ttk.Button(bar, text="Nova", command=self.new_order).pack(side="left", padx=4)
        ttk.Button(bar, text="Cancelar", command=self.cancel_order).pack(side="left", padx=4)
        ttk.Button(bar, text="Duplicar", command=self.duplicate_order).pack(side="left", padx=4)
        self.tree = ttk.Treeview(self, columns=("numero", "estado", "total"), show="headings")
        for c in ("numero", "estado", "total"):
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for o in self.order_service.list_all():
            self.tree.insert("", "end", iid=o["id"], values=(o["numero"], o["estado_producao"], o["total_cents"]))

    def open_order(self, order_id: str):
        order, items = self.order_service.get_with_items(order_id)
        OrderEditorDialog(self, self.order_service, self.client_service, self.product_service, existing_order=order, existing_items=items)
        self.refresh()

    def new_order(self):
        OrderEditorDialog(self, self.order_service, self.client_service, self.product_service)
        self.refresh()

    def cancel_order(self):
        sel = self.tree.selection()
        if not sel:
            return
        self.order_service.cancel(sel[0])
        self.refresh()

    def duplicate_order(self):
        sel = self.tree.selection()
        if not sel:
            return
        self.order_service.duplicate(sel[0])
        self.refresh()
