import tkinter as tk
from tkinter import ttk

from app.config import APP_ICON, COLOR_MAIN_BG
from app.product_service import (
    create_product,
    get_product,
    list_categories,
    list_manufacturers,
    list_suppliers,
    list_units,
    update_product,
)
from app.ui.styles import set_window_icon
from app.ui.widgets import choose_image, show_error, show_info


class ProductForm(tk.Toplevel):
    def __init__(self, parent, product_id=None, on_saved=None):
        super().__init__(parent)
        self.product_id = product_id
        self.on_saved = on_saved
        self.image_path = None
        self.title('Редактирование товара' if product_id else 'Добавление товара')
        self.configure(bg=COLOR_MAIN_BG)
        self.geometry('720x620')
        self.resizable(False, False)
        set_window_icon(self, APP_ICON)

        self.categories = list_categories()
        self.manufacturers = list_manufacturers()
        self.suppliers = list_suppliers()
        self.units = list_units()

        self.category_by_name = {item['category_name']: item['category_id'] for item in self.categories}
        self.manufacturer_by_name = {item['manufacturer_name']: item['manufacturer_id'] for item in self.manufacturers}
        self.supplier_by_name = {item['supplier_name']: item['supplier_id'] for item in self.suppliers}
        self.unit_by_name = {item['unit_name']: item['unit_id'] for item in self.units}

        self._build_ui()
        if product_id:
            self._load_product(product_id)
        self.grab_set()
        self.focus_set()

    def _build_ui(self):
        header = ttk.Label(self, text=self.title(), style='Header.TLabel')
        header.pack(fill='x', padx=12, pady=(12, 8))

        form = ttk.Frame(self)
        form.pack(fill='both', expand=True, padx=12, pady=8)
        form.columnconfigure(1, weight=1)

        self.article_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.manufacturer_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.price_var = tk.StringVar(value='0')
        self.unit_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value='0')
        self.discount_var = tk.StringVar(value='0')
        self.image_var = tk.StringVar(value='Изображение не выбрано')

        fields = [
            ('Артикул товара', ttk.Entry(form, textvariable=self.article_var)),
            ('Наименование товара', ttk.Entry(form, textvariable=self.name_var)),
            ('Категория товара', ttk.Combobox(form, textvariable=self.category_var, values=list(self.category_by_name), state='readonly')),
            ('Описание товара', ttk.Entry(form, textvariable=self.description_var)),
            ('Производитель', ttk.Combobox(form, textvariable=self.manufacturer_var, values=list(self.manufacturer_by_name), state='readonly')),
            ('Поставщик', ttk.Combobox(form, textvariable=self.supplier_var, values=list(self.supplier_by_name), state='readonly')),
            ('Цена', ttk.Entry(form, textvariable=self.price_var)),
            ('Единица измерения', ttk.Combobox(form, textvariable=self.unit_var, values=list(self.unit_by_name), state='readonly')),
            ('Количество на складе', ttk.Entry(form, textvariable=self.quantity_var)),
            ('Действующая скидка, %', ttk.Entry(form, textvariable=self.discount_var)),
        ]

        for row, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', padx=6, pady=6)
            widget.grid(row=row, column=1, sticky='ew', padx=6, pady=6)

        ttk.Label(form, text='Фото товара').grid(row=len(fields), column=0, sticky='w', padx=6, pady=6)
        image_frame = ttk.Frame(form)
        image_frame.grid(row=len(fields), column=1, sticky='ew', padx=6, pady=6)
        ttk.Label(image_frame, textvariable=self.image_var).pack(side='left', fill='x', expand=True)
        ttk.Button(image_frame, text='Выбрать фото', command=self._choose_image).pack(side='right')

        buttons = ttk.Frame(self)
        buttons.pack(fill='x', padx=12, pady=12)
        ttk.Button(buttons, text='Сохранить', style='Accent.TButton', command=self._save).pack(side='right', padx=6)
        ttk.Button(buttons, text='Назад', command=self.destroy).pack(side='right', padx=6)

    def _load_product(self, product_id):
        product = get_product(product_id)
        if not product:
            show_error('Ошибка', 'Товар не найден.')
            self.destroy()
            return
        self.article_var.set(product['article'])
        self.name_var.set(product['product_name'])
        self.category_var.set(product['category_name'])
        self.description_var.set(product['description'])
        self.manufacturer_var.set(product['manufacturer_name'])
        self.supplier_var.set(product['supplier_name'])
        self.price_var.set(str(product['price']))
        self.unit_var.set(product['unit_name'])
        self.quantity_var.set(str(product['quantity']))
        self.discount_var.set(str(product['discount_percent']))
        self.image_path = product.get('image_path')
        self.image_var.set(self.image_path or 'Изображение не выбрано')

    def _choose_image(self):
        try:
            new_path = choose_image(self.image_path)
            if new_path:
                self.image_path = new_path
                self.image_var.set(new_path)
        except Exception as exc:
            show_error('Ошибка загрузки изображения', str(exc))

    def _collect_data(self):
        return {
            'article': self.article_var.get(),
            'product_name': self.name_var.get(),
            'category_id': self.category_by_name.get(self.category_var.get()),
            'description': self.description_var.get(),
            'manufacturer_id': self.manufacturer_by_name.get(self.manufacturer_var.get()),
            'supplier_id': self.supplier_by_name.get(self.supplier_var.get()),
            'price': self.price_var.get(),
            'unit_id': self.unit_by_name.get(self.unit_var.get()),
            'quantity': self.quantity_var.get(),
            'discount_percent': self.discount_var.get(),
            'image_path': self.image_path,
        }

    def _save(self):
        try:
            data = self._collect_data()
            if self.product_id:
                update_product(self.product_id, data)
                show_info('Сохранено', 'Данные товара обновлены.')
            else:
                create_product(data)
                show_info('Сохранено', 'Товар добавлен.')
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as exc:
            show_error('Ошибка сохранения', str(exc))
