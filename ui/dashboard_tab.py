from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class DashboardTab(ttk.Frame):
    def __init__(self, master, dashboard_service, open_order_callback):
        super().__init__(master)
        self.dashboard_service = dashboard_service
        self.open_order_callback = open_order_callback
        self.kpi_label = ttk.Label(self, text="")
        self.kpi_label.pack(anchor="w", padx=10, pady=10)
        self.tree = ttk.Treeview(self, columns=("numero", "estado", "total"), show="headings", height=12)
        for c in ("numero", "estado", "total"):
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self._open)
        self.refresh()

    def refresh(self):
        k = self.dashboard_service.kpis()
        self.kpi_label.config(text=f"Pendentes: {k['pendentes']} | Abertas: {k['encomendas_abertas']} | Stock baixo: {k['stock_baixo']}")
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for order in self.dashboard_service.recent_orders(15):
            self.tree.insert("", "end", iid=order["id"], values=(order["numero"], order["estado_producao"], order["total_cents"]))

    def _open(self, _event):
        sel = self.tree.selection()
        if sel:
            self.open_order_callback(sel[0])
