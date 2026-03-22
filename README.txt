# SquackTS Enterprise (POD)

Aplicação desktop local, single-user e offline-first para gestão operacional Print-on-Demand.
Tema padrão: escuro, com alternância claro/escuro na topbar.

## Arquitectura
- db.py + schema.py: persistência SQLite com WAL e foreign keys.
- repositories/: SQL puro sem regras de negócio.
- services/: validações, transações e auditoria.
- ui/: Tkinter modular com shell SaaS (sidebar + topbar), cards e modo escuro obrigatório.

## Execução
1. `python -m venv .venv`
2. `.venv\\Scripts\\activate`
3. `pip install -r requirements.txt`
4. `python app.py`

Alternativa Windows: `Iniciar App.bat`

## Paths
- Projecto default: `C:\Users\lopes\Downloads\Squackts`
- DB default: `%LOCALAPPDATA%\SquackTS_Enterprise\data\squackts_enterprise.db`
- Imagens: `images/`
- Backups: `backups/squackts_enterprise_backup_YYYYMMDD_HHMMSS.db`

Nota: evitar pastas sincronizadas (ex: OneDrive) para reduzir conflitos de locks.

## Restauro manual de backup
Fechar a aplicação e copiar o ficheiro de backup para o caminho da BD activa.

## Checklist de validações
- Email/NIF (9 dígitos) em clientes.
- Quantidade > 0, preços e custos >= 0.
- SKU único em produtos.
- Cancelamento idempotente via `stock_returned`.
- `PRAGMA user_version` definido no schema.

## Mermaid timeline
```mermaid
timeline
    title Desenvolvimento SquackTS
    Fase 1 : Estrutura base
    Fase 2 : Schema e DB
    Fase 3 : Repositories
    Fase 4 : Services
    Fase 5 : UI principal
    Fase 6 : Diálogos
    Fase 7 : Backups e logs
    Fase 8 : Scripts PS1
    Fase 9 : Validação final
```

## Comparativo de padrões
| Plataforma | Packing slip/branding | Workflow/rules | Tracking |
|---|---|---|---|
| SquackTS Enterprise | Sim (campo e fluxo local) | Sim (estados e regras locais) | Sim (manual) |
| Printful | Sim | Parcial | Sim |
| Gelato | Sim | Parcial | Sim |
| Order Desk | N/A | Sim (regras avançadas) | Sim |

## Fontes oficiais
- Python sqlite3 backup: https://docs.python.org/3/library/sqlite3.html
- SQLite foreign keys: https://sqlite.org/foreignkeys.html
- SQLite WAL: https://sqlite.org/wal.html
- Pillow Image.convert: https://pillow.readthedocs.io/en/stable/reference/Image.html
- Microsoft Expand-Archive: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.archive/expand-archive
- Microsoft WSH shortcuts: https://learn.microsoft.com/pt-br/troubleshoot/windows-client/admin-development/create-desktop-shortcut-with-wsh
- Printful packing slips: https://help.printful.com/hc/en-us/articles/360014065499-What-does-the-packing-slip-look-like
- Gelato branded packaging: https://dashboard.gelato.com/docs/guides/branded-packaging-guide/
- Order Desk rules: https://help.orderdesk.com/order-desk-101/how-to-work-with-rules/
