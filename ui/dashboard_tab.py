from __future__ import annotations

from tkinter import ttk


class DashboardTab(ttk.Frame):
    page_key = "painel"

    def __init__(self, master, dashboard_service, open_order_callback):
        super().__init__(master, style="App.TFrame", padding=12)
        self.dashboard_service = dashboard_service
        self.open_order_callback = open_order_callback

        self.kpi_wrap = ttk.Frame(self, style="App.TFrame")
        self.kpi_wrap.pack(fill="x", pady=(0, 10))

        content = ttk.Panedwindow(self, orient="horizontal")
        content.pack(fill="both", expand=True)

        left = ttk.Frame(content, style="App.TFrame")
        right = ttk.Frame(content, style="App.TFrame")
        content.add(left, weight=4)
        content.add(right, weight=2)

        recent_box = ttk.Labelframe(left, text="Encomendas recentes", style="Card.TLabelframe", padding=10)
        recent_box.pack(fill="both", expand=True)
        self.recent_tree = ttk.Treeview(
            recent_box,
            columns=("numero", "estado", "pago", "total", "prevista"),
            show="headings",
            height=14,
        )
        for col, title, width in [
            ("numero", "Numero", 120),
            ("estado", "Producao", 120),
            ("pago", "Pago", 70),
            ("total", "Total", 90),
            ("prevista", "Prevista", 110),
        ]:
            self.recent_tree.heading(col, text=title)
            self.recent_tree.column(col, width=width, anchor="w")
        self.recent_tree.pack(fill="both", expand=True)
        self.recent_tree.bind("<Double-1>", self._open_order)

        alert_box = ttk.Labelframe(right, text="Resumo operacional", style="Card.TLabelframe", padding=10)
        alert_box.pack(fill="both", expand=True)
        self.alerts = ttk.Treeview(alert_box, columns=("tipo", "valor"), show="headings", height=8)
        self.alerts.heading("tipo", text="Indicador")
        self.alerts.heading("valor", text="Valor")
        self.alerts.column("tipo", width=180)
        self.alerts.column("valor", width=80)
        self.alerts.pack(fill="both", expand=True)

        quick_box = ttk.Labelframe(right, text="Acoes rapidas", style="Card.TLabelframe", padding=10)
        quick_box.pack(fill="x", pady=(10, 0))
        ttk.Button(quick_box, text="Abrir encomenda selecionada", command=self._open_selected, style="Ghost.TButton").pack(fill="x")

        self.refresh()

    def header(self) -> tuple[str, str]:
        return "Painel", "Resumo operacional de vendas, producao e expedicao"

    def actions(self):
        return [("Atualizar", self.refresh, "Ghost.TButton")]

    def on_search(self, query: str):
        self.refresh(query=query)

    def refresh(self, query: str = ""):
        for child in self.kpi_wrap.winfo_children():
            child.destroy()
        kpi = self.dashboard_service.kpis()
        cards = [
            ("Encomendas hoje", str(kpi.get("encomendas_hoje", 0)), "Registos criados hoje"),
            ("Por pagar", str(kpi.get("por_pagar", 0)), "Comercial confirmada sem pagamento"),
            ("Pagas por produzir", str(kpi.get("pagas_por_produzir", 0)), "Pagas e pendentes"),
            ("Em producao", str(kpi.get("em_producao", 0)), "Ordens em fabrico"),
            ("Prontas a enviar", str(kpi.get("prontas_envio", 0)), "Aguardam expedicao"),
            ("Atrasadas", str(kpi.get("atrasadas", 0)), "Data prevista ultrapassada"),
            ("Faturado do mes", kpi.get("faturado_mes", "0.00 EUR"), "Total confirmado no mes"),
            ("Ticket medio", kpi.get("ticket_medio", "0.00 EUR"), "Media por encomenda"),
        ]
        for idx, (title, value, subtitle) in enumerate(cards):
            card = ttk.Frame(self.kpi_wrap, style="Surface.TFrame", padding=10)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")
            self.kpi_wrap.columnconfigure(idx, weight=1)
            ttk.Label(card, text=title, style="Muted.TLabel").pack(anchor="w")
            ttk.Label(card, text=value, style="Title.TLabel").pack(anchor="w")
            ttk.Label(card, text=subtitle, style="Muted.TLabel").pack(anchor="w")

        for iid in self.recent_tree.get_children():
            self.recent_tree.delete(iid)
        for row in self.dashboard_service.recent_orders(30, query=query):
            self.recent_tree.insert(
                "",
                "end",
                iid=row["id"],
                values=(
                    row["numero"],
                    row["estado_producao"],
                    "Sim" if row["pago"] else "Nao",
                    f"{row['total_cents'] / 100:.2f} EUR",
                    row["data_prevista"] or "-",
                ),
            )

        for iid in self.alerts.get_children():
            self.alerts.delete(iid)
        alerts = [
            ("Stock baixo", kpi.get("stock_baixo", 0)),
            ("Sem tracking", kpi.get("sem_tracking", 0)),
            ("Pendentes", kpi.get("pendentes", 0)),
        ]
        for item in alerts:
            self.alerts.insert("", "end", values=item)

    def _open_order(self, _event):
        self._open_selected()

    def _open_selected(self):
        sel = self.recent_tree.selection()
        if sel:
            self.open_order_callback(sel[0])
