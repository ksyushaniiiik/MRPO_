from pathlib import Path
from typing import Any, Iterable, Optional

from .db import get_connection, get_or_create_id


PRODUCT_SELECT = '''
SELECT p.product_id, p.article, p.product_name, p.description, p.price, p.quantity,
       p.discount_percent, p.image_path,
       c.category_id, c.category_name,
       m.manufacturer_id, m.manufacturer_name,
       s.supplier_id, s.supplier_name,
       u.unit_id, u.unit_name,
       ROUND(p.price * (1 - p.discount_percent / 100.0), 2) AS final_price
FROM products p
JOIN categories c ON c.category_id = p.category_id
JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
JOIN suppliers s ON s.supplier_id = p.supplier_id
JOIN units u ON u.unit_id = p.unit_id
'''


def list_products(search: str = '', supplier_id: Optional[int] = None, sort_mode: str = '') -> list[dict]:
    where = []
    params: list[Any] = []
    search = (search or '').strip()
    if search:
        pattern = f'%{search}%'
        where.append(
            '''(
                p.article LIKE ? OR p.product_name LIKE ? OR p.description LIKE ? OR
                c.category_name LIKE ? OR m.manufacturer_name LIKE ? OR
                s.supplier_name LIKE ? OR u.unit_name LIKE ?
            )'''
        )
        params.extend([pattern] * 7)
    if supplier_id:
        where.append('p.supplier_id = ?')
        params.append(supplier_id)
    query = PRODUCT_SELECT
    if where:
        query += ' WHERE ' + ' AND '.join(where)
    if sort_mode == 'quantity_asc':
        query += ' ORDER BY p.quantity ASC, p.product_name ASC'
    elif sort_mode == 'quantity_desc':
        query += ' ORDER BY p.quantity DESC, p.product_name ASC'
    else:
        query += ' ORDER BY p.product_name ASC'
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def get_product(product_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(PRODUCT_SELECT + ' WHERE p.product_id = ?', (product_id,)).fetchone()
        return dict(row) if row else None


def list_suppliers() -> list[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name')]


def list_categories() -> list[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT category_id, category_name FROM categories ORDER BY category_name')]


def list_manufacturers() -> list[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT manufacturer_id, manufacturer_name FROM manufacturers ORDER BY manufacturer_name')]


def list_units() -> list[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT unit_id, unit_name FROM units ORDER BY unit_name')]


def validate_product(data: dict) -> None:
    required = ['article', 'product_name', 'category_id', 'manufacturer_id', 'supplier_id', 'unit_id']
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise ValueError('Заполните обязательные поля товара.')
    try:
        price = float(data.get('price', 0))
        quantity = int(data.get('quantity', 0))
        discount = float(data.get('discount_percent', 0))
    except ValueError as exc:
        raise ValueError('Цена, количество и скидка должны быть числами.') from exc
    if price < 0:
        raise ValueError('Цена товара не может быть отрицательной.')
    if quantity < 0:
        raise ValueError('Количество на складе не может быть отрицательным.')
    if discount < 0 or discount > 100:
        raise ValueError('Скидка должна быть в диапазоне от 0 до 100%.')


def create_product(data: dict) -> int:
    validate_product(data)
    with get_connection() as conn:
        cur = conn.execute(
            '''
            INSERT INTO products(
                article, product_name, category_id, description, manufacturer_id,
                supplier_id, price, unit_id, quantity, discount_percent, image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['article'].strip(), data['product_name'].strip(), data.get('category_id'),
                data.get('description', '').strip(), data.get('manufacturer_id'), data.get('supplier_id'),
                float(data.get('price', 0)), data.get('unit_id'), int(data.get('quantity', 0)),
                float(data.get('discount_percent', 0)), data.get('image_path'),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_product(product_id: int, data: dict) -> None:
    validate_product(data)
    with get_connection() as conn:
        conn.execute(
            '''
            UPDATE products
            SET article = ?, product_name = ?, category_id = ?, description = ?, manufacturer_id = ?,
                supplier_id = ?, price = ?, unit_id = ?, quantity = ?, discount_percent = ?, image_path = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = ?
            ''',
            (
                data['article'].strip(), data['product_name'].strip(), data.get('category_id'),
                data.get('description', '').strip(), data.get('manufacturer_id'), data.get('supplier_id'),
                float(data.get('price', 0)), data.get('unit_id'), int(data.get('quantity', 0)),
                float(data.get('discount_percent', 0)), data.get('image_path'), product_id,
            ),
        )
        conn.commit()


def product_used_in_orders(product_id: int) -> bool:
    with get_connection() as conn:
        row = conn.execute('SELECT 1 FROM order_items WHERE product_id = ? LIMIT 1', (product_id,)).fetchone()
        return bool(row)


def delete_product(product_id: int) -> None:
    if product_used_in_orders(product_id):
        raise ValueError('Товар нельзя удалить, потому что он присутствует в заказе.')
    with get_connection() as conn:
        conn.execute('DELETE FROM products WHERE product_id = ?', (product_id,))
        conn.commit()


def ensure_lookup_by_name(table: str, id_col: str, name_col: str, name: str) -> int:
    with get_connection() as conn:
        value = get_or_create_id(conn, table, id_col, name_col, name)
        conn.commit()
        return value
