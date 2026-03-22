from __future__ import annotations

from dataclasses import dataclass
from tkinter import ttk


@dataclass(frozen=True)
class Palette:
    bg: str
    surface: str
    text: str
    muted: str
    border: str
    primary: str
    primary_hover: str
    success: str
    warning: str
    danger: str
    dark: str
    sidebar_text: str


LIGHT = Palette(
    bg="#F6F7F9",
    surface="#FFFFFF",
    text="#111827",
    muted="#6B7280",
    border="#E5E7EB",
    primary="#2563EB",
    primary_hover="#1D4ED8",
    success="#059669",
    warning="#D97706",
    danger="#DC2626",
    dark="#1F2937",
    sidebar_text="#E5E7EB",
)

DARK = Palette(
    bg="#0F172A",
    surface="#111827",
    text="#E5E7EB",
    muted="#94A3B8",
    border="#334155",
    primary="#3B82F6",
    primary_hover="#2563EB",
    success="#10B981",
    warning="#F59E0B",
    danger="#EF4444",
    dark="#020617",
    sidebar_text="#CBD5E1",
)


def get_palette(mode: str) -> Palette:
    return DARK if mode == "dark" else LIGHT


def apply_theme(root, mode: str = "dark") -> None:
    palette = get_palette(mode)
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(bg=palette.bg)

    style.configure("App.TFrame", background=palette.bg)
    style.configure("Surface.TFrame", background=palette.surface, relief="flat")
    style.configure("Sidebar.TFrame", background=palette.dark)
    style.configure("Topbar.TFrame", background=palette.surface)

    style.configure("Title.TLabel", background=palette.surface, foreground=palette.text, font=("Segoe UI", 15, "bold"))
    style.configure("Subtitle.TLabel", background=palette.surface, foreground=palette.muted, font=("Segoe UI", 10))
    style.configure("Body.TLabel", background=palette.surface, foreground=palette.text, font=("Segoe UI", 10))
    style.configure("Muted.TLabel", background=palette.surface, foreground=palette.muted, font=("Segoe UI", 9))
    style.configure("Sidebar.TLabel", background=palette.dark, foreground=palette.sidebar_text, font=("Segoe UI", 10))
    style.configure("SidebarTitle.TLabel", background=palette.dark, foreground=palette.text, font=("Segoe UI", 12, "bold"))

    style.configure("TButton", font=("Segoe UI", 10), padding=(10, 6), background=palette.surface, foreground=palette.text)
    style.configure("Primary.TButton", background=palette.primary, foreground="#FFFFFF", borderwidth=0)
    style.map("Primary.TButton", background=[("active", palette.primary_hover)])
    style.configure("Danger.TButton", background=palette.danger, foreground="#FFFFFF", borderwidth=0)
    style.map("Danger.TButton", background=[("active", "#B91C1C")])
    style.configure("Ghost.TButton", background=palette.surface, foreground=palette.text, bordercolor=palette.border)

    style.configure("Card.TLabelframe", background=palette.surface, bordercolor=palette.border, relief="solid")
    style.configure("Card.TLabelframe.Label", background=palette.surface, foreground=palette.text, font=("Segoe UI", 10, "bold"))

    style.configure("TEntry", fieldbackground=palette.surface, foreground=palette.text, bordercolor=palette.border, padding=6)
    style.configure("TCombobox", fieldbackground=palette.surface, foreground=palette.text, padding=4)
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 9), background=palette.surface, fieldbackground=palette.surface, foreground=palette.text)
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background=palette.bg, foreground=palette.text)
