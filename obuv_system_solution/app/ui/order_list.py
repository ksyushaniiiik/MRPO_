import tkinter as tk
from tkinter import ttk

from app.config import COLOR_MAIN_BG, FONT_FAMILY
from app.order_service import delete_order, list_orders
from app.ui.order_form import OrderForm
from app.ui.widgets import ScrollableFrame, ask_yes_no, show_error, show_info


class OrderListFrame(ttk.Frame):
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        self.user = user
        self.can_manage = user.get('role_code') == 'admin'
        self.form_window = None
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        title_row = ttk.Frame(self)
        title_row.pack(fill='x', pady=(0, 8))
        ttk.Label(title_row, text='Список заказов', style='Header.TLabel').pack(side='left', fill='x', expand=True)
        if self.can_manage:
            ttk.Button(title_row, text='Добавить заказ', style='Accent.TButton', command=self._open_create_form).pack(side='right')
        self.list_frame = ScrollableFrame(self, bg=COLOR_MAIN_BG)
        self.list_frame.pack(fill='both', expand=True)

    def refresh(self):
        for child in self.list_frame.inner.winfo_children():
            child.destroy()
        orders = list_orders()
        if not orders:
            ttk.Label(self.list_frame.inner, text='Заказы не найдены.').pack(anchor='w', padx=12, pady=12)
            return
        for order in orders:
            self._render_order_card(order)

    def _render_order_card(self, order):
        card = tk.Frame(self.list_frame.inner, bg=COLOR_MAIN_BG, bd=2, relief='groove')
        card.pack(fill='x', padx=8, pady=6)
        card.columnconfigure(0, weight=1)
        left = tk.Frame(card, bg=COLOR_MAIN_BG)
        left.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        info = [
            f"Артикул заказа: {order['order_article']}",
            f"Статус заказа: {order['status_name']}",
            f"Адрес пункта выдачи: {order['pickup_point_address']}",
            f"Дата заказа: {order['order_date']}",
            f"Позиций в заказе: {order['items_count']} | Сумма: {order['total_sum']:.2f} ₽",
        ]
        for index, text in enumerate(info):
            font = (FONT_FAMILY, 11, 'bold') if index == 0 else (FONT_FAMILY, 11)
            tk.Label(left, text=text, bg=COLOR_MAIN_BG, font=font, anchor='w').pack(anchor='w')

        right = tk.Frame(card, bg=COLOR_MAIN_BG, bd=1, relief='solid')
        right.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        tk.Label(right, text='Дата поставки', bg=COLOR_MAIN_BG, font=(FONT_FAMILY, 11, 'bold')).pack(padx=16, pady=(16, 4))
        tk.Label(right, text=order['delivery_date'] or 'Не указана', bg=COLOR_MAIN_BG, font=(FONT_FAMILY, 11)).pack(padx=16, pady=(0, 16))

        if self.can_manage:
            actions = tk.Frame(card, bg=COLOR_MAIN_BG)
            actions.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)
            ttk.Button(actions, text='Редактировать', command=lambda o=order: self._open_edit_form(o['order_id'])).pack(fill='x', pady=2)
            ttk.Button(actions, text='Удалить', command=lambda o=order: self._delete_order(o['order_id'])).pack(fill='x', pady=2)

    def _open_create_form(self):
        self._open_form(None)

    def _open_edit_form(self, order_id):
        self._open_form(order_id)

    def _open_form(self, order_id):
        if self.form_window and self.form_window.winfo_exists():
            self.form_window.focus_set()
            show_info('Окно уже открыто', 'Закройте текущее окно редактирования заказа перед открытием нового.')
            return
        self.form_window = OrderForm(self, order_id=order_id, on_saved=self.refresh)

    def _delete_order(self, order_id):
        if not ask_yes_no('Подтверждение удаления', 'Удалить выбранный заказ? Операцию нельзя отменить.'):
            return
        try:
            delete_order(order_id)
            self.refresh()
            show_info('Удалено', 'Заказ удален.')
        except Exception as exc:
            show_error('Ошибка удаления', str(exc))
