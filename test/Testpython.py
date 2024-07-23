import pandas as pd
import pandasql as psql
import json

# Функция для загрузки данных из JSON файлов в DataFrame
def load_data():
    base_path = r'C:\Users\TEMP.HOME-PC.004\PycharmProjects\SQL_Tester_new_Version_v1\my_app\data\\'
    files = {
        'warehouses': 'WAREHOUSES.json',
        'products': 'PRODUCTS.json',
        'orders': 'ORDERS.json',
        'order_line': 'ORDER_LINE.json',
        'lost': 'LOST.json'
    }

    data = {name: pd.read_json(f"{base_path}{filename}") for name, filename in files.items()}
    return data

# Загрузка данных
data = load_data()

# Приведём все имена продуктов к нижнему регистру (если требуется)
if 'products' in data:
    data['products']['name'] = data['products']['name'].str.lower()

# Пример SQL-запроса: вывести имя и срок годности продуктов, содержащих слово 'самокат' в назвах, если их срок годности не превышает 7 дней
query = """
SELECT name, shelf_life
FROM products
WHERE LOWER(name) LIKE '%самокат%'
  AND shelf_life <= 7;
"""

# Выполнение SQL-запроса к DataFrame
result = psql.sqldf(query, data)

# Создание словаря для записи в JSON файл
output = {
    "query": query,
    "result": result.to_dict(orient='records')
}

# Запись результатов в JSON файл
output_path = r"C:\Users\TEMP.HOME-PC.004\PycharmProjects\SQL_Tester_new_Version_v1\test\Task_2.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)

# Вывод результатов для проверки в терминале
print(result)
