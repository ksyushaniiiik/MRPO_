import tkinter as tk
from tkinter import ttk

from app.config import (
    COLOR_DISCOUNT_OVER_15,
    COLOR_MAIN_BG,
    COLOR_OUT_OF_STOCK,
    COLOR_SECONDARY_BG,
    FONT_FAMILY,
)
from app.product_service import delete_product, list_products, list_suppliers
from app.ui.product_form import ProductForm
from app.ui.widgets import ScrollableFrame, ask_yes_no, load_tk_image, show_error, show_info


class ProductListFrame(ttk.Frame):
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        self.user = user
        self.role_code = user.get('role_code')
        self.can_manage = self.role_code == 'admin'
        self.can_search = self.role_code in {'admin', 'manager'}
        self.supplier_map = {'Все поставщики': None}
        self.image_refs = []
        self.form_window = None

        self.search_var = tk.StringVar()
        self.supplier_var = tk.StringVar(value='Все поставщики')
        self.sort_var = tk.StringVar(value='Без сортировки')
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        title_row = ttk.Frame(self)
        title_row.pack(fill='x', pady=(0, 8))
        ttk.Label(title_row, text='Список товаров', style='Header.TLabel').pack(side='left', fill='x', expand=True)
        if self.can_manage:
            ttk.Button(title_row, text='Добавить товар', style='Accent.TButton', command=self._open_create_form).pack(side='right')

        if self.can_search:
            controls = ttk.Frame(self)
            controls.pack(fill='x', pady=(0, 8))

            ttk.Label(controls, text='Поиск').pack(side='left', padx=(0, 6))
            search_entry = ttk.Entry(controls, textvariable=self.search_var, width=30)
            search_entry.pack(side='left', padx=(0, 12))

            for supplier in list_suppliers():
                self.supplier_map[supplier['supplier_name']] = supplier['supplier_id']
            ttk.Label(controls, text='Поставщик').pack(side='left', padx=(0, 6))
            supplier_combo = ttk.Combobox(
                controls,
                textvariable=self.supplier_var,
                values=list(self.supplier_map),
                state='readonly',
                width=22,
            )
            supplier_combo.pack(side='left', padx=(0, 12))

            ttk.Label(controls, text='Сортировка').pack(side='left', padx=(0, 6))
            sort_combo = ttk.Combobox(
                controls,
                textvariable=self.sort_var,
                values=['Без сортировки', 'Количество ↑', 'Количество ↓'],
                state='readonly',
                width=18,
            )
            sort_combo.pack(side='left')

            self.search_var.trace_add('write', lambda *_: self.refresh())
            self.supplier_var.trace_add('write', lambda *_: self.refresh())
            self.sort_var.trace_add('write', lambda *_: self.refresh())

        self.list_frame = ScrollableFrame(self, bg=COLOR_MAIN_BG)
        self.list_frame.pack(fill='both', expand=True)

    def refresh(self):
        for child in self.list_frame.inner.winfo_children():
            child.destroy()
        self.image_refs.clear()

        sort_map = {
            'Количество ↑': 'quantity_asc',
            'Количество ↓': 'quantity_desc',
        }
        products = list_products(
            search=self.search_var.get() if self.can_search else '',
            supplier_id=self.supplier_map.get(self.supplier_var.get()) if self.can_search else None,
            sort_mode=sort_map.get(self.sort_var.get(), ''),
        )
        if not products:
            ttk.Label(self.list_frame.inner, text='Товары не найдены.').pack(anchor='w', padx=12, pady=12)
            return
        for product in products:
            self._render_product_card(product)

    def _card_bg(self, product):
        if int(product['quantity']) == 0:
            return COLOR_OUT_OF_STOCK
        if float(product['discount_percent']) > 15:
            return COLOR_DISCOUNT_OVER_15
        return COLOR_MAIN_BG

    def _render_product_card(self, product):
        bg = self._card_bg(product)
        card = tk.Frame(self.list_frame.inner, bg=bg, bd=2, relief='groove')
        card.pack(fill='x', padx=8, pady=6)
        card.columnconfigure(1, weight=1)

        image = load_tk_image(product.get('image_path'))
        self.image_refs.append(image)
        image_label = tk.Label(card, image=image, text='Фото' if not image else '', width=130, height=90, bg=bg)
        image_label.grid(row=0, column=0, rowspan=6, sticky='nsew', padx=8, pady=8)

        title = f"{product['category_name']} | {product['product_name']}"
        tk.Label(card, text=title, bg=bg, font=(FONT_FAMILY, 12, 'bold'), anchor='w').grid(row=0, column=1, sticky='ew', padx=8, pady=(8, 2))
        details = [
            f"Описание товара: {product['description']}",
            f"Производитель: {product['manufacturer_name']}",
            f"Поставщик: {product['supplier_name']}",
            f"Единица измерения: {product['unit_name']}",
            f"Количество на складе: {product['quantity']}",
        ]
        for idx, text in enumerate(details, start=1):
            tk.Label(card, text=text, bg=bg, font=(FONT_FAMILY, 11), anchor='w').grid(row=idx, column=1, sticky='ew', padx=8, pady=1)

        price_frame = tk.Frame(card, bg=bg)
        price_frame.grid(row=6, column=1, sticky='w', padx=8, pady=(2, 8))
        tk.Label(price_frame, text='Цена: ', bg=bg, font=(FONT_FAMILY, 11, 'bold')).pack(side='left')
        if float(product['discount_percent']) > 0:
            tk.Label(
                price_frame,
                text=f"{product['price']:.2f} ₽",
                bg=bg,
                fg='red',
                font=(FONT_FAMILY, 11, 'overstrike'),
            ).pack(side='left', padx=(0, 8))
            tk.Label(price_frame, text=f"{product['final_price']:.2f} ₽", bg=bg, fg='black', font=(FONT_FAMILY, 11, 'bold')).pack(side='left')
        else:
            tk.Label(price_frame, text=f"{product['price']:.2f} ₽", bg=bg, fg='black', font=(FONT_FAMILY, 11, 'bold')).pack(side='left')

        discount = tk.Label(
            card,
            text=f"Действующая скидка\n{product['discount_percent']:.0f}%",
            bg=bg,
            font=(FONT_FAMILY, 11, 'bold'),
            width=16,
        )
        discount.grid(row=0, column=2, rowspan=4, sticky='nsew', padx=8, pady=8)

        if self.can_manage:
            actions = tk.Frame(card, bg=bg)
            actions.grid(row=4, column=2, rowspan=3, sticky='nsew', padx=8, pady=8)
            ttk.Button(actions, text='Редактировать', command=lambda p=product: self._open_edit_form(p['product_id'])).pack(fill='x', pady=2)
            ttk.Button(actions, text='Удалить', command=lambda p=product: self._delete_product(p['product_id'])).pack(fill='x', pady=2)

    def _open_create_form(self):
        self._open_form(None)

    def _open_edit_form(self, product_id):
        self._open_form(product_id)

    def _open_form(self, product_id):
        if self.form_window and self.form_window.winfo_exists():
            self.form_window.focus_set()
            show_info('Окно уже открыто', 'Закройте текущее окно редактирования товара перед открытием нового.')
            return
        self.form_window = ProductForm(self, product_id=product_id, on_saved=self.refresh)

    def _delete_product(self, product_id):
        if not ask_yes_no('Подтверждение удаления', 'Удалить выбранный товар? Операцию нельзя отменить.'):
            return
        try:
            delete_product(product_id)
            self.refresh()
            show_info('Удалено', 'Товар удален.')
        except Exception as exc:
            show_error('Ошибка удаления', str(exc))
