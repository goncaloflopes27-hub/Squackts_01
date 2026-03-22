from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from repositories import logs as logs_repo
from ui.clients_tab import ClientsTab
from ui.dashboard_tab import DashboardTab
from ui.orders_tab import OrdersTab
from ui.products_tab import ProductsTab
from ui.production_tab import ProductionTab
from ui.system_tab import SystemTab


class MainWindow(tk.Tk):
    def __init__(self, container):
        super().__init__()
        self.title("SquackTS Enterprise")
        self.geometry("1100x700")
        self.container = container
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.orders_tab = OrdersTab(nb, container.order_service, container.client_service, container.product_service)
        self.dashboard_tab = DashboardTab(nb, container.dashboard_service, self.orders_tab.open_order)
        nb.add(self.dashboard_tab, text="Início")
        nb.add(self.orders_tab, text="Encomendas")
        nb.add(ProductsTab(nb, container.product_service), text="Produtos")
        nb.add(ClientsTab(nb, container.client_service), text="Clientes")
        nb.add(ProductionTab(nb, container.production_service), text="Produção")
        nb.add(SystemTab(nb, container.backup_service, logs_repo, container.conn), text="Sistema")
