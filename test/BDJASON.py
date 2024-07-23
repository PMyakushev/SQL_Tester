import os
import json
import sqlite3

# Пути к папке с JSON-файлами и базе данных
json_folder_path = r"C:\Users\pmyakishev\SQL_Tester_final\my_app\data"
db_path = r"C:\Users\pmyakishev\SQL_Tester_final\my_app\your_database.db"

# Подключение к базе данных
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Создание таблиц, если они еще не существуют
cursor.execute('''
CREATE TABLE IF NOT EXISTS lost (
    date TEXT,
    warehouse_id INTEGER,
    product_id INTEGER,     
    item_id INTEGER,
    quantity REAL,
    amount REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS order_line (
    order_id INTEGER,
    date TEXT,
    warehouse_id INTEGER,
    product_id INTEGER,
    price REAL,
    regular_price REAL,
    cost_price REAL,
    quantity REAL,
    paid_amount REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER,
    warehouse_id INTEGER,
    user_id INTEGER,
    date TEXT,
    paid_amount REAL,
    quantity REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER,
    name TEXT,
    group1 TEXT,
    group2 TEXT,
    group3 TEXT,
    weight REAL,
    shelf_life INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id INTEGER,
    name TEXT,
    city TEXT,
    date_open TEXT,
    date_close TEXT
)
''')

# Функция для вставки данных в таблицу
def insert_data(table, data):
    if isinstance(data, dict):
        keys = ', '.join(data.keys())
        question_marks = ', '.join(['?'] * len(data))
        values = tuple(data.values())
        cursor.execute(f"INSERT INTO {table} ({keys}) VALUES ({question_marks})", values)
    elif isinstance(data, list):
        for item in data:
            keys = ', '.join(item.keys())
            question_marks = ', '.join(['?'] * len(item))
            values = tuple(item.values())
            cursor.execute(f"INSERT INTO {table} ({keys}) VALUES ({question_marks})", values)
    else:
        raise ValueError("Data must be a dictionary or a list of dictionaries")

# Обработка каждого JSON-файла и вставка данных в соответствующую таблицу
json_files = {
    'LOST.json': 'lost',
    'ORDER_LINE.json': 'order_line',
    'ORDERS.json': 'orders',
    'PRODUCTS.json': 'products',
    'WAREHOUSES.json': 'warehouses'
}

for filename, table in json_files.items():
    file_path = os.path.join(json_folder_path, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            # Преобразование формата даты
            for item in json_data:
                if 'date' in item:
                    item['date'] = item['date'].replace('T', ' ').replace('Z', '')
                if table == 'products' and 'name' in item:
                    item['name'] = item['name'].lower()
            insert_data(table, json_data)
    else:
        print(f"File {filename} does not exist.")

# Сохранение изменений и закрытие соединения с базой данных
conn.commit()
conn.close()
