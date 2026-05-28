PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_code TEXT NOT NULL UNIQUE,
    role_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    last_name TEXT NOT NULL,
    first_name TEXT NOT NULL,
    patronymic TEXT DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS manufacturers (
    manufacturer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    manufacturer_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    unit_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    discount_percent REAL NOT NULL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    image_path TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);

CREATE TABLE IF NOT EXISTS order_statuses (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS pickup_points (
    pickup_point_id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_article TEXT NOT NULL UNIQUE,
    status_id INTEGER NOT NULL,
    pickup_point_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    delivery_date TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (status_id) REFERENCES order_statuses(status_id),
    FOREIGN KEY (pickup_point_id) REFERENCES pickup_points(pickup_point_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_quantity ON products(quantity);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(product_name);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status_id);
