from __future__ import annotations

from tkinter import ttk


class ProductionTab(ttk.Frame):
    page_key = "producao"

    def __init__(self, master, production_service):
        super().__init__(master, style="App.TFrame", padding=12)
        self.production_service = production_service
        self.segment = ttk.Combobox(self, values=["pendente", "em_producao", "produzida", "pronta_envio"], width=18)
        self.segment.set("pendente")
        self.segment.pack(anchor="w", pady=(0, 8))
        self.segment.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        box = ttk.Labelframe(self, text="Fila de producao", style="Card.TLabelframe", padding=8)
        box.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(box, columns=("numero", "cliente", "item", "qtd", "tipo", "prazo", "estado"), show="headings")
        for c, t, w in [
            ("numero", "Encomenda", 120),
            ("cliente", "Cliente", 150),
            ("item", "Item", 160),
            ("qtd", "Qtd", 60),
            ("tipo", "Tipo", 110),
            ("prazo", "Prazo", 90),
            ("estado", "Estado", 100),
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True)

        footer = ttk.Frame(self, style="App.TFrame")
        footer.pack(fill="x", pady=(8, 0))
        ttk.Button(footer, text="Marcar pendente", command=lambda: self._set("pendente"), style="Ghost.TButton").pack(side="left", padx=4)
        ttk.Button(footer, text="Em producao", command=lambda: self._set("em_producao"), style="Primary.TButton").pack(side="left", padx=4)
        ttk.Button(footer, text="Produzida", command=lambda: self._set("produzida"), style="Ghost.TButton").pack(side="left", padx=4)
        ttk.Button(footer, text="Pronta a enviar", command=lambda: self._set("pronta_envio"), style="Ghost.TButton").pack(side="left", padx=4)
        self.refresh()

    def header(self) -> tuple[str, str]:
        return "Producao", "Fila operacional por prioridade e estado"

    def actions(self):
        return [("Atualizar fila", self.refresh, "Ghost.TButton")]

    def on_search(self, query: str):
        self.refresh(query=query)

    def refresh(self, query: str = ""):
        status = self.segment.get() if hasattr(self, "segment") else "pendente"
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for row in self.production_service.queue(status=status, query=query):
            self.tree.insert(
                "",
                "end",
                iid=f"{row['order_id']}::{row['item_id']}",
                values=(
                    row["numero"],
                    row["client_nome"] or "-",
                    row["nome_snapshot"],
                    row["quantidade"],
                    row["tipo_producao_snapshot"],
                    row["data_prevista"] or "-",
                    row["estado_producao"],
                ),
            )

    def _set(self, status: str):
        sel = self.tree.selection()
        if not sel:
            return
        order_id = sel[0].split("::", 1)[0]
        self.production_service.set_status(order_id, status)
        self.refresh()
