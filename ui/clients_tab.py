from __future__ import annotations

from tkinter import ttk

from ui.dialogs.client_editor import ClientEditorDialog


class ClientsTab(ttk.Frame):
    page_key = "clientes"

    def __init__(self, master, client_service, order_service):
        super().__init__(master, style="App.TFrame", padding=12)
        self.client_service = client_service
        self.order_service = order_service

        pane = ttk.Panedwindow(self, orient="horizontal")
        pane.pack(fill="both", expand=True)

        left = ttk.Labelframe(pane, text="Lista de clientes", style="Card.TLabelframe", padding=8)
        right = ttk.Labelframe(pane, text="Perfil do cliente", style="Card.TLabelframe", padding=10)
        pane.add(left, weight=4)
        pane.add(right, weight=3)

        self.tree = ttk.Treeview(left, columns=("nome", "email", "telefone", "nif"), show="headings")
        for c, t, w in [("nome", "Nome", 180), ("email", "Email", 180), ("telefone", "Telefone", 110), ("nif", "NIF", 90)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._update_detail)
        self.tree.bind("<Double-1>", self.edit_selected)

        self.detail = ttk.Label(right, text="Selecione um cliente para detalhe.", style="Body.TLabel", justify="left")
        self.detail.pack(fill="x")

        self.refresh()

    def header(self) -> tuple[str, str]:
        return "Clientes", "Dados do cliente, contacto e historico comercial"

    def actions(self):
        return [("Novo cliente", self.new_client, "Primary.TButton")]

    def on_search(self, query: str):
        self.refresh(query=query)

    def refresh(self, query: str = ""):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for c in self.client_service.list_all(query=query):
            self.tree.insert("", "end", iid=c["id"], values=(c["nome"], c["email"], c["telefone"], c["nif"]))

    def new_client(self):
        ClientEditorDialog(self, self.client_service)
        self.refresh()

    def edit_selected(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        client = self.client_service.get_by_id(sel[0])
        if client:
            ClientEditorDialog(self, self.client_service, existing=dict(client))
            self.refresh()

    def _update_detail(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            self.detail.config(text="Selecione um cliente para detalhe.")
            return
        c = self.client_service.get_by_id(sel[0])
        if not c:
            return
        recent = self.order_service.list_by_client(c["id"], limit=5)
        lines = [
            f"{c['nome']}",
            f"Email: {c['email'] or '-'}",
            f"Telefone: {c['telefone'] or '-'}",
            f"NIF: {c['nif'] or '-'}",
            f"Morada: {c['morada'] or '-'}",
            f"Notas: {c['notas'] or '-'}",
            "Encomendas recentes:",
        ]
        for o in recent:
            lines.append(f"- {o['numero']} | {o['estado_producao']} | {o['total_cents'] / 100:.2f} EUR")
        self.detail.config(text="\n".join(lines))
