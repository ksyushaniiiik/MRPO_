import tkinter as tk
from tkinter import ttk

from app.auth import authenticate, full_name, guest_user
from app.config import APP_ICON, APP_TITLE, COLOR_MAIN_BG, COLOR_SECONDARY_BG
from app.db import ensure_database
from app.ui.order_list import OrderListFrame
from app.ui.product_list import ProductListFrame
from app.ui.styles import apply_style, set_window_icon
from app.ui.widgets import show_error


class ShoeStoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        ensure_database()
        self.title(APP_TITLE)
        self.geometry('1100x720')
        self.minsize(900, 600)
        apply_style(self)
        set_window_icon(self, APP_ICON)
        self.current_user = None
        self.content = None
        self.header = None
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.current_user = None
        self.clear()
        self.title(f'{APP_TITLE} — вход')
        outer = ttk.Frame(self)
        outer.place(relx=0.5, rely=0.5, anchor='center')

        ttk.Label(outer, text='ООО «Обувь»', style='Header.TLabel').grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 18))
        ttk.Label(outer, text='Логин').grid(row=1, column=0, sticky='w', padx=6, pady=6)
        ttk.Label(outer, text='Пароль').grid(row=2, column=0, sticky='w', padx=6, pady=6)

        login_var = tk.StringVar()
        password_var = tk.StringVar()
        login_entry = ttk.Entry(outer, textvariable=login_var, width=28)
        password_entry = ttk.Entry(outer, textvariable=password_var, width=28, show='*')
        login_entry.grid(row=1, column=1, padx=6, pady=6)
        password_entry.grid(row=2, column=1, padx=6, pady=6)

        def login_action():
            user = authenticate(login_var.get(), password_var.get())
            if not user:
                show_error('Ошибка авторизации', 'Неверный логин или пароль. Проверьте данные и попробуйте снова.')
                return
            self.show_main(user)

        buttons = ttk.Frame(outer)
        buttons.grid(row=3, column=0, columnspan=2, pady=16)
        ttk.Button(buttons, text='Войти', style='Accent.TButton', command=login_action).pack(side='left', padx=6)
        ttk.Button(buttons, text='Войти как гость', command=lambda: self.show_main(guest_user())).pack(side='left', padx=6)
        ttk.Label(
            outer,
            text='Тестовые пользователи: admin/admin123, manager/manager123, client/client123',
        ).grid(row=4, column=0, columnspan=2, pady=(8, 0))
        login_entry.focus_set()
        self.bind('<Return>', lambda _event: login_action())

    def show_main(self, user: dict):
        self.unbind('<Return>')
        self.current_user = user
        self.clear()
        self.title(f'{APP_TITLE} — {user.get("role_name")}')
        self._build_header()
        self.content = ttk.Frame(self)
        self.content.pack(fill='both', expand=True, padx=12, pady=12)
        self.show_products()

    def _build_header(self):
        self.header = ttk.Frame(self, style='Header.TFrame')
        self.header.pack(fill='x')
        ttk.Label(self.header, text='ООО «Обувь»', style='Header.TLabel').pack(side='left', padx=12, pady=10)
        ttk.Label(
            self.header,
            text=f"{full_name(self.current_user)} | {self.current_user.get('role_name')}",
            style='User.TLabel',
        ).pack(side='right', padx=12, pady=10)
        ttk.Button(self.header, text='Выход', command=self.show_login).pack(side='right', padx=8, pady=10)
        if self.current_user.get('role_code') in {'admin', 'manager'}:
            ttk.Button(self.header, text='Заказы', command=self.show_orders).pack(side='right', padx=8, pady=10)
        ttk.Button(self.header, text='Товары', command=self.show_products).pack(side='right', padx=8, pady=10)

    def _replace_content(self, frame_cls):
        for widget in self.content.winfo_children():
            widget.destroy()
        frame = frame_cls(self.content, self.current_user)
        frame.pack(fill='both', expand=True)

    def show_products(self):
        self._replace_content(ProductListFrame)

    def show_orders(self):
        if self.current_user.get('role_code') not in {'admin', 'manager'}:
            show_error('Доступ запрещен', 'Просмотр заказов доступен только менеджеру и администратору.')
            return
        self._replace_content(OrderListFrame)


def main():
    app = ShoeStoreApp()
    app.mainloop()


if __name__ == '__main__':
    main()
