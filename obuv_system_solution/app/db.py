import hashlib
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from .config import DATABASE_PATH, BASE_DIR

SCHEMA_PATH = BASE_DIR / 'database' / 'schema.sql'
SEED_PATH = BASE_DIR / 'database' / 'seed.sql'


def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def execute_script(path: Path) -> None:
    with get_connection() as conn:
        conn.executescript(path.read_text(encoding='utf-8'))
        conn.commit()


def ensure_database() -> None:
    execute_script(SCHEMA_PATH)
    execute_script(SEED_PATH)
    seed_users()
    seed_products_and_orders()


def get_or_create_id(conn: sqlite3.Connection, table: str, id_col: str, name_col: str, value: str) -> int:
    value = (value or 'Не указано').strip()
    row = conn.execute(f'SELECT {id_col} FROM {table} WHERE {name_col} = ?', (value,)).fetchone()
    if row:
        return int(row[id_col])
    cur = conn.execute(f'INSERT INTO {table}({name_col}) VALUES (?)', (value,))
    return int(cur.lastrowid)


def seed_users() -> None:
    users = [
        ('admin', 'admin123', 'admin', 'Иванов', 'Андрей', 'Петрович'),
        ('manager', 'manager123', 'manager', 'Петрова', 'Мария', 'Игоревна'),
        ('client', 'client123', 'client', 'Сидоров', 'Сергей', 'Олегович'),
    ]
    with get_connection() as conn:
        for login, pwd, role_code, last_name, first_name, patronymic in users:
            role = conn.execute('SELECT role_id FROM roles WHERE role_code = ?', (role_code,)).fetchone()
            if not role:
                continue
            conn.execute(
                '''
                INSERT OR IGNORE INTO users(role_id, login, password_hash, last_name, first_name, patronymic)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (role['role_id'], login, password_hash(pwd), last_name, first_name, patronymic),
            )
        conn.commit()


def seed_products_and_orders() -> None:
    products = [
        ('SH-001', 'Кроссовки городские Comfort Run', 'Кроссовки', 'Легкие повседневные кроссовки для города', 'ООО СпортШуз', 'Поставщик Альфа', 4990.00, 'пара', 12, 10, 'images/sample_1.png'),
        ('SH-002', 'Ботинки зимние Nord', 'Ботинки', 'Утепленные ботинки с нескользящей подошвой', 'Фабрика Север', 'Поставщик Бета', 8490.00, 'пара', 6, 20, 'images/sample_2.png'),
        ('SH-003', 'Туфли классические Black Line', 'Туфли', 'Классическая модель для делового стиля', 'StepLine', 'Поставщик Гамма', 6990.00, 'пара', 0, 5, 'images/sample_3.png'),
        ('SH-004', 'Сандалии летние Breeze', 'Сандалии', 'Открытая летняя модель для ежедневной носки', 'ИП Комфорт', 'Поставщик Альфа', 2990.50, 'пара', 18, 0, 'images/sample_4.png'),
    ]
    with get_connection() as conn:
        unit_default = get_or_create_id(conn, 'units', 'unit_id', 'unit_name', 'пара')
        for article, name, category, desc, manufacturer, supplier, price, unit, quantity, discount, image_path in products:
            category_id = get_or_create_id(conn, 'categories', 'category_id', 'category_name', category)
            manufacturer_id = get_or_create_id(conn, 'manufacturers', 'manufacturer_id', 'manufacturer_name', manufacturer)
            supplier_id = get_or_create_id(conn, 'suppliers', 'supplier_id', 'supplier_name', supplier)
            unit_id = get_or_create_id(conn, 'units', 'unit_id', 'unit_name', unit) or unit_default
            conn.execute(
                '''
                INSERT OR IGNORE INTO products(
                    article, product_name, category_id, description, manufacturer_id,
                    supplier_id, price, unit_id, quantity, discount_percent, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (article, name, category_id, desc, manufacturer_id, supplier_id, price, unit_id, quantity, discount, image_path),
            )

        order_count = conn.execute('SELECT COUNT(*) AS cnt FROM orders').fetchone()['cnt']
        if order_count == 0:
            status_id = get_or_create_id(conn, 'order_statuses', 'status_id', 'status_name', 'В обработке')
            pickup_id = get_or_create_id(conn, 'pickup_points', 'pickup_point_id', 'address', 'Москва, ул. Пушкина, д. 1')
            cur = conn.execute(
                '''
                INSERT INTO orders(order_article, status_id, pickup_point_id, order_date, delivery_date)
                VALUES (?, ?, ?, ?, ?)
                ''',
                ('ORD-001', status_id, pickup_id, '2026-02-10', '2026-02-14'),
            )
            product = conn.execute('SELECT product_id, price FROM products WHERE article = ?', ('SH-001',)).fetchone()
            if product:
                conn.execute(
                    'INSERT INTO order_items(order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)',
                    (cur.lastrowid, product['product_id'], 1, product['price']),
                )
        conn.commit()
