import tkinter as tk
from tkinter import ttk

from app.config import APP_ICON, COLOR_MAIN_BG
from app.order_service import (
    create_order,
    get_order,
    list_pickup_points,
    list_statuses,
    update_order,
)
from app.ui.styles import set_window_icon
from app.ui.widgets import show_error, show_info


class OrderForm(tk.Toplevel):
    def __init__(self, parent, order_id=None, on_saved=None):
        super().__init__(parent)
        self.order_id = order_id
        self.on_saved = on_saved
        self.title('Редактирование заказа' if order_id else 'Добавление заказа')
        self.configure(bg=COLOR_MAIN_BG)
        self.geometry('640x380')
        self.resizable(False, False)
        set_window_icon(self, APP_ICON)

        self.statuses = list_statuses()
        self.pickup_points = list_pickup_points()
        self.status_by_name = {item['status_name']: item['status_id'] for item in self.statuses}
        self.pickup_by_address = {item['address']: item['pickup_point_id'] for item in self.pickup_points}

        self._build_ui()
        if order_id:
            self._load_order(order_id)
        self.grab_set()
        self.focus_set()

    def _build_ui(self):
        ttk.Label(self, text=self.title(), style='Header.TLabel').pack(fill='x', padx=12, pady=(12, 8))
        form = ttk.Frame(self)
        form.pack(fill='both', expand=True, padx=12, pady=8)
        form.columnconfigure(1, weight=1)

        self.article_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.pickup_var = tk.StringVar()
        self.order_date_var = tk.StringVar()
        self.delivery_date_var = tk.StringVar()

        fields = [
            ('Артикул заказа', ttk.Entry(form, textvariable=self.article_var)),
            ('Статус заказа', ttk.Combobox(form, textvariable=self.status_var, values=list(self.status_by_name), state='readonly')),
            ('Адрес пункта выдачи', ttk.Combobox(form, textvariable=self.pickup_var, values=list(self.pickup_by_address), state='readonly')),
            ('Дата заказа, ГГГГ-ММ-ДД', ttk.Entry(form, textvariable=self.order_date_var)),
            ('Дата выдачи, ГГГГ-ММ-ДД', ttk.Entry(form, textvariable=self.delivery_date_var)),
        ]
        for row, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', padx=6, pady=8)
            widget.grid(row=row, column=1, sticky='ew', padx=6, pady=8)

        buttons = ttk.Frame(self)
        buttons.pack(fill='x', padx=12, pady=12)
        ttk.Button(buttons, text='Сохранить', style='Accent.TButton', command=self._save).pack(side='right', padx=6)
        ttk.Button(buttons, text='Назад', command=self.destroy).pack(side='right', padx=6)

    def _load_order(self, order_id):
        order = get_order(order_id)
        if not order:
            show_error('Ошибка', 'Заказ не найден.')
            self.destroy()
            return
        self.article_var.set(order['order_article'])
        self.status_var.set(order['status_name'])
        self.pickup_var.set(order['pickup_point_address'])
        self.order_date_var.set(order['order_date'])
        self.delivery_date_var.set(order['delivery_date'] or '')

    def _collect_data(self):
        return {
            'order_article': self.article_var.get(),
            'status_id': self.status_by_name.get(self.status_var.get()),
            'pickup_point_id': self.pickup_by_address.get(self.pickup_var.get()),
            'order_date': self.order_date_var.get(),
            'delivery_date': self.delivery_date_var.get(),
        }

    def _save(self):
        try:
            data = self._collect_data()
            if self.order_id:
                update_order(self.order_id, data)
                show_info('Сохранено', 'Данные заказа обновлены.')
            else:
                create_order(data)
                show_info('Сохранено', 'Заказ добавлен.')
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as exc:
            show_error('Ошибка сохранения', str(exc))
