import sqlite3
import pandas as pd


# Подключение к базе данных SQLite
db_path = r'C:\Users\TEMP.HOME-PC.004\PycharmProjects\SQL_Tester_new_Version_v1\my_app\your_database.db'
conn = sqlite3.connect(db_path)

# Пример SQL-запроса: вывести количество складов и среднее количество товаров на один склад для каждого города за июнь 2020 года
query = """
SELECT name, shelf_life
FROM products
WHERE LOWER(name) LIKE '%самокат%'
  AND shelf_life <= 7;
"""

# Выполнение SQL-запроса к базе данных
result = pd.read_sql_query(query, conn)

# Вывод результатов
print(result)

# Закрытие соединения
conn.close()
