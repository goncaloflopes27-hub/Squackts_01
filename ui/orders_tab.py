from __future__ import annotations

from tkinter import messagebox, ttk

from ui.dialogs.order_editor import OrderEditorDialog


class OrdersTab(ttk.Frame):
    page_key = "encomendas"

    def __init__(self, master, order_service, client_service, product_service):
        super().__init__(master, style="App.TFrame", padding=12)
        self.order_service = order_service
        self.client_service = client_service
        self.product_service = product_service

        filter_row = ttk.Frame(self, style="App.TFrame")
        filter_row.pack(fill="x", pady=(0, 8))
        self.estado_var = ttk.Combobox(filter_row, values=["todos", "pendente", "em_producao", "produzida", "pronta_envio"], width=16)
        self.estado_var.set("todos")
        self.estado_var.pack(side="left", padx=(0, 8))
        self.pago_var = ttk.Combobox(filter_row, values=["todos", "pago", "nao_pago"], width=12)
        self.pago_var.set("todos")
        self.pago_var.pack(side="left", padx=(0, 8))
        ttk.Button(filter_row, text="Aplicar filtros", command=self.refresh, style="Ghost.TButton").pack(side="left")

        pane = ttk.Panedwindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True)

        left = ttk.Labelframe(pane, text="Lista de encomendas", style="Card.TLabelframe", padding=8)
        right = ttk.Labelframe(pane, text="Detalhe da encomenda", style="Card.TLabelframe", padding=10)
        pane.add(left, weight=4)
        pane.add(right, weight=3)

        self.tree = ttk.Treeview(
            left,
            columns=("numero", "cliente", "estado", "pago", "tracking", "total", "prevista", "created"),
            show="headings",
        )
        columns = [
            ("numero", "Numero", 120),
            ("cliente", "Cliente", 180),
            ("estado", "Producao", 110),
            ("pago", "Pago", 70),
            ("tracking", "Tracking", 120),
            ("total", "Total", 90),
            ("prevista", "Prevista", 95),
            ("created", "Criada", 95),
        ]
        for key, title, width in columns:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._update_detail)
        self.tree.bind("<Double-1>", lambda _e: self.open_selected())

        self.detail = ttk.Label(right, text="Selecione uma encomenda para ver contexto.", style="Body.TLabel", justify="left")
        self.detail.pack(anchor="nw", fill="x")

        self.refresh()

    def header(self) -> tuple[str, str]:
        return "Encomendas", "Acompanhe pagamentos, producao e expedicao"

    def actions(self):
        return [
            ("Nova encomenda", self.new_order, "Primary.TButton"),
            ("Duplicar", self.duplicate_order, "Ghost.TButton"),
            ("Cancelar", self.cancel_order, "Danger.TButton"),
        ]

    def on_search(self, query: str):
        self.refresh(query=query)

    def refresh(self, query: str = ""):
        estado = self.estado_var.get() if hasattr(self, "estado_var") else "todos"
        pago = self.pago_var.get() if hasattr(self, "pago_var") else "todos"
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for o in self.order_service.list_all(query=query, estado=estado, pago=pago):
            self.tree.insert(
                "",
                "end",
                iid=o["id"],
                values=(
                    o["numero"],
                    o["client_nome"] or "-",
                    o["estado_producao"],
                    "Sim" if o["pago"] else "Nao",
                    o["tracking"] or "Sem tracking",
                    f"{o['total_cents'] / 100:.2f} EUR",
                    o["data_prevista"] or "-",
                    (o["created_at"] or "")[:10],
                ),
            )

    def open_order(self, order_id: str):
        order, items = self.order_service.get_with_items(order_id)
        if not order:
            return
        OrderEditorDialog(self, self.order_service, self.client_service, self.product_service, existing_order=order, existing_items=items)
        self.refresh()

    def open_selected(self):
        sel = self.tree.selection()
        if sel:
            self.open_order(sel[0])

    def new_order(self):
        OrderEditorDialog(self, self.order_service, self.client_service, self.product_service)
        self.refresh()

    def cancel_order(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Confirmar", "Cancelar encomenda selecionada?", parent=self):
            return
        self.order_service.cancel(sel[0])
        self.refresh()

    def duplicate_order(self):
        sel = self.tree.selection()
        if not sel:
            return
        self.order_service.duplicate(sel[0])
        self.refresh()

    def _update_detail(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            self.detail.config(text="Selecione uma encomenda para ver contexto.")
            return
        order, items = self.order_service.get_with_items(sel[0])
        if not order:
            return
        lines = [
            f"{order['numero']}  |  {order['estado_comercial']} / {order['estado_producao']}",
            f"Cliente: {order['client_id']}",
            f"Pagamento: {'Pago' if order['pago'] else 'Nao pago'}",
            f"Tracking: {order['tracking'] or 'Sem tracking'}",
            f"Resumo financeiro: {order['subtotal_cents'] / 100:.2f} + {order['portes_cents'] / 100:.2f} = {order['total_cents'] / 100:.2f} EUR",
            "Itens da encomenda:",
        ]
        for it in items:
            lines.append(f"- {it['sku_snapshot']} x{it['quantidade']} [{it['tipo_producao_snapshot']}]")
        lines.append(f"Notas: {order['notas'] or '-'}")
        self.detail.config(text="\n".join(lines))
