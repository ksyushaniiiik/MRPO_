import tkinter as tk
from tkinter import ttk

from app.config import (
    FONT_FAMILY,
    COLOR_MAIN_BG,
    COLOR_SECONDARY_BG,
    COLOR_ACCENT,
)


def apply_style(root: tk.Tk) -> None:
    root.configure(bg=COLOR_MAIN_BG)
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    default_font = (FONT_FAMILY, 11)
    header_font = (FONT_FAMILY, 16, 'bold')
    button_font = (FONT_FAMILY, 11, 'bold')

    style.configure('.', font=default_font, background=COLOR_MAIN_BG)
    style.configure('TFrame', background=COLOR_MAIN_BG)
    style.configure('Header.TFrame', background=COLOR_SECONDARY_BG)
    style.configure('TLabel', font=default_font, background=COLOR_MAIN_BG)
    style.configure('Header.TLabel', font=header_font, background=COLOR_SECONDARY_BG)
    style.configure('User.TLabel', font=(FONT_FAMILY, 10, 'bold'), background=COLOR_SECONDARY_BG)
    style.configure('TButton', font=button_font, padding=6)
    style.configure('Accent.TButton', background=COLOR_ACCENT, font=button_font, padding=6)
    style.configure('TEntry', font=default_font)
    style.configure('TCombobox', font=default_font)
    style.configure('Treeview', font=default_font, rowheight=28)
    style.configure('Treeview.Heading', font=(FONT_FAMILY, 11, 'bold'))


def set_window_icon(window: tk.Tk | tk.Toplevel, icon_path) -> None:
    try:
        icon = tk.PhotoImage(file=str(icon_path))
        window.iconphoto(True, icon)
        window._icon_ref = icon
    except Exception:
        pass
