from __future__ import annotations

from tkinter import ttk

from ui.dialogs.client_editor import ClientEditorDialog


class ClientsTab(ttk.Frame):
    def __init__(self, master, client_service):
        super().__init__(master)
        self.client_service = client_service
        ttk.Button(self, text="Novo cliente", command=self.new_client).pack(anchor="w", padx=8, pady=8)
        self.tree = ttk.Treeview(self, columns=("nome", "email", "nif"), show="headings")
        for c in ("nome", "email", "nif"):
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.edit_selected)
        self.refresh()

    def refresh(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for c in self.client_service.list_all():
            self.tree.insert("", "end", iid=c["id"], values=(c["nome"], c["email"], c["nif"]))

    def new_client(self):
        ClientEditorDialog(self, self.client_service)
        self.refresh()

    def edit_selected(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        client = next((x for x in self.client_service.list_all() if x["id"] == sel[0]), None)
        if client:
            ClientEditorDialog(self, self.client_service, existing=dict(client))
            self.refresh()
