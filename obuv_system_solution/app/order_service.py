from typing import Optional

from .db import get_connection, get_or_create_id


ORDER_SELECT = '''
SELECT o.order_id, o.order_article, o.order_date, o.delivery_date,
       os.status_id, os.status_name,
       pp.pickup_point_id, pp.address AS pickup_point_address,
       COUNT(oi.order_item_id) AS items_count,
       ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 2) AS total_sum
FROM orders o
JOIN order_statuses os ON os.status_id = o.status_id
JOIN pickup_points pp ON pp.pickup_point_id = o.pickup_point_id
LEFT JOIN order_items oi ON oi.order_id = o.order_id
'''


def list_orders() -> list[dict]:
    query = ORDER_SELECT + ' GROUP BY o.order_id ORDER BY o.order_date DESC, o.order_id DESC'
    with get_connection() as conn:
        return [dict(row) for row in conn.execute(query).fetchall()]


def get_order(order_id: int) -> Optional[dict]:
    query = ORDER_SELECT + ' WHERE o.order_id = ? GROUP BY o.order_id'
    with get_connection() as conn:
        row = conn.execute(query, (order_id,)).fetchone()
        if not row:
            return None
        order = dict(row)
        items = conn.execute(
            '''
            SELECT oi.order_item_id, oi.product_id, oi.quantity, oi.unit_price,
                   p.article, p.product_name
            FROM order_items oi
            JOIN products p ON p.product_id = oi.product_id
            WHERE oi.order_id = ?
            ORDER BY oi.order_item_id
            ''',
            (order_id,),
        ).fetchall()
        order['items'] = [dict(item) for item in items]
        return order


def list_statuses() -> list[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT status_id, status_name FROM order_statuses ORDER BY status_id')]


def list_pickup_points() -> list[dict]:
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('SELECT pickup_point_id, address FROM pickup_points ORDER BY address')]


def validate_order(data: dict) -> None:
    if not data.get('order_article'):
        raise ValueError('Укажите артикул заказа.')
    if not data.get('status_id'):
        raise ValueError('Выберите статус заказа.')
    if not data.get('pickup_point_id'):
        raise ValueError('Выберите адрес пункта выдачи.')
    if not data.get('order_date'):
        raise ValueError('Укажите дату заказа.')


def create_order(data: dict) -> int:
    validate_order(data)
    with get_connection() as conn:
        cur = conn.execute(
            '''
            INSERT INTO orders(order_article, status_id, pickup_point_id, order_date, delivery_date)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                data['order_article'].strip(), data['status_id'], data['pickup_point_id'],
                data['order_date'].strip(), data.get('delivery_date', '').strip() or None,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def update_order(order_id: int, data: dict) -> None:
    validate_order(data)
    with get_connection() as conn:
        conn.execute(
            '''
            UPDATE orders
            SET order_article = ?, status_id = ?, pickup_point_id = ?, order_date = ?,
                delivery_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = ?
            ''',
            (
                data['order_article'].strip(), data['status_id'], data['pickup_point_id'],
                data['order_date'].strip(), data.get('delivery_date', '').strip() or None, order_id,
            ),
        )
        conn.commit()


def delete_order(order_id: int) -> None:
    with get_connection() as conn:
        conn.execute('DELETE FROM orders WHERE order_id = ?', (order_id,))
        conn.commit()
