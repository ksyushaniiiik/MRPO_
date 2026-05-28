INSERT OR IGNORE INTO roles(role_code, role_name) VALUES
('client', 'Клиент'),
('manager', 'Менеджер'),
('admin', 'Администратор');

INSERT OR IGNORE INTO categories(category_name) VALUES
('Кроссовки'), ('Ботинки'), ('Туфли'), ('Сандалии');

INSERT OR IGNORE INTO manufacturers(manufacturer_name) VALUES
('ООО СпортШуз'), ('ИП Комфорт'), ('Фабрика Север'), ('StepLine');

INSERT OR IGNORE INTO suppliers(supplier_name) VALUES
('Поставщик Альфа'), ('Поставщик Бета'), ('Поставщик Гамма');

INSERT OR IGNORE INTO units(unit_name) VALUES
('пара'), ('шт.');

INSERT OR IGNORE INTO order_statuses(status_name) VALUES
('Новый'), ('В обработке'), ('Готов к выдаче'), ('Выдан'), ('Отменен');

INSERT OR IGNORE INTO pickup_points(address) VALUES
('Москва, ул. Пушкина, д. 1'),
('Москва, пр-т Мира, д. 10'),
('Казань, ул. Баумана, д. 25');
