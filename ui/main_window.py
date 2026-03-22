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
from ui.theme import apply_theme, get_palette


class MainWindow(tk.Tk):
    def __init__(self, container):
        super().__init__()
        self.title("SquackTS Enterprise")
        self.geometry("1360x820")
        self.minsize(1200, 740)
        self.theme_mode = "dark"
        apply_theme(self, self.theme_mode)

        self.container = container
        self.current_page = None
        self.page_frames: dict[str, ttk.Frame] = {}

        root = ttk.Frame(self, style="App.TFrame")
        root.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(root, style="Sidebar.TFrame", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ttk.Label(self.sidebar, text="SquackTS Enterprise", style="SidebarTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 2))
        ttk.Label(self.sidebar, text="Operacoes POD", style="Sidebar.TLabel").pack(anchor="w", padx=14, pady=(0, 16))

        self.nav_buttons = {}
        nav_items = [
            ("painel", "Painel"),
            ("encomendas", "Encomendas"),
            ("catalogo", "Catalogo"),
            ("clientes", "Clientes"),
            ("producao", "Producao"),
            ("sistema", "Sistema"),
        ]
        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=label,
                anchor="w",
                relief="flat",
                borderwidth=0,
                font=("Segoe UI", 10, "bold"),
                padx=14,
                pady=8,
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[key] = btn

        ttk.Label(self.sidebar, text="v1.1 local", style="Sidebar.TLabel").pack(side="bottom", anchor="w", padx=14, pady=14)

        content = ttk.Frame(root, style="App.TFrame")
        content.pack(side="left", fill="both", expand=True)

        self.topbar = ttk.Frame(content, style="Topbar.TFrame", padding=(16, 10))
        self.topbar.pack(fill="x", padx=10, pady=10)
        self.title_lbl = ttk.Label(self.topbar, text="", style="Title.TLabel")
        self.title_lbl.pack(anchor="w")
        self.subtitle_lbl = ttk.Label(self.topbar, text="", style="Subtitle.TLabel")
        self.subtitle_lbl.pack(anchor="w")

        top_actions = ttk.Frame(self.topbar, style="Topbar.TFrame")
        top_actions.pack(fill="x", pady=(8, 0))
        self.search_var = tk.StringVar()
        search = ttk.Entry(top_actions, textvariable=self.search_var, width=40)
        search.pack(side="left")
        search.bind("<Return>", lambda _e: self._apply_search())
        ttk.Button(top_actions, text="Alternar tema", command=self.toggle_theme, style="Ghost.TButton").pack(side="right", padx=4)
        self.actions_bar = ttk.Frame(top_actions, style="Topbar.TFrame")
        self.actions_bar.pack(side="right")

        self.page_host = ttk.Frame(content, style="App.TFrame")
        self.page_host.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.page_frames = {
            "painel": DashboardTab(self.page_host, container.dashboard_service, self.open_order),
            "encomendas": OrdersTab(self.page_host, container.order_service, container.client_service, container.product_service),
            "catalogo": ProductsTab(self.page_host, container.product_service),
            "clientes": ClientsTab(self.page_host, container.client_service, container.order_service),
            "producao": ProductionTab(self.page_host, container.production_service),
            "sistema": SystemTab(self.page_host, container.backup_service, logs_repo, container.conn),
        }
        self.bind("<Control-f>", lambda _e: search.focus_set())
        self.show_page("painel")

    def _refresh_nav_colors(self) -> None:
        palette = get_palette(self.theme_mode)
        for page_key, btn in self.nav_buttons.items():
            btn.configure(
                bg="#334155" if page_key == self.current_page else palette.dark,
                fg=palette.sidebar_text,
                activebackground="#475569",
                activeforeground="#FFFFFF",
            )

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        apply_theme(self, self.theme_mode)
        self._refresh_nav_colors()

    def show_page(self, key: str):
        if self.current_page:
            self.page_frames[self.current_page].pack_forget()
        self.current_page = key
        self._refresh_nav_colors()
        page = self.page_frames[key]
        page.pack(fill="both", expand=True)
        title, subtitle = page.header()
        self.title_lbl.config(text=title)
        self.subtitle_lbl.config(text=subtitle)
        for child in self.actions_bar.winfo_children():
            child.destroy()
        for label, callback, style in page.actions():
            ttk.Button(self.actions_bar, text=label, command=callback, style=style).pack(side="right", padx=4)
        self._apply_search()

    def _apply_search(self):
        if self.current_page:
            self.page_frames[self.current_page].on_search(self.search_var.get().strip())

    def open_order(self, order_id: str):
        self.show_page("encomendas")
        orders_page: OrdersTab = self.page_frames["encomendas"]
        orders_page.open_order(order_id)
