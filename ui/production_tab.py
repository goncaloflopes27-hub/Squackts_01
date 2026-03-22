from __future__ import annotations

from tkinter import ttk


class ProductionTab(ttk.Frame):
    def __init__(self, master, production_service):
        super().__init__(master)
        self.production_service = production_service
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=6)
        ttk.Button(bar, text="Em produção", command=lambda: self._set("em_producao")).pack(side="left", padx=4)
        ttk.Button(bar, text="Produzida", command=lambda: self._set("produzida")).pack(side="left", padx=4)
        ttk.Button(bar, text="Pronta envio", command=lambda: self._set("pronta_envio")).pack(side="left", padx=4)
        self.tree = ttk.Treeview(self, columns=("numero", "estado"), show="headings")
        self.tree.heading("numero", text="numero")
        self.tree.heading("estado", text="estado")
        self.tree.pack(fill="both", expand=True)
        self.refresh()

    def refresh(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for o in self.production_service.queue():
            self.tree.insert("", "end", iid=o["id"], values=(o["numero"], o["estado_producao"]))

    def _set(self, status: str):
        sel = self.tree.selection()
        if not sel:
            return
        self.production_service.set_status(sel[0], status)
        self.refresh()
