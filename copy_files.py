import subprocess

# Путь откуда забираем файлы
source_path = 'св/'Ядыкин Алексей'/*.json'

# Путь куда копируем файлы
destination_path = '/opt/SQL_Tester/my_app/ResultEtalon/'

# Команда cp для копирования файлов с заменой
cp_command = f'cp -rf {source_path} {destination_path}'

try:
    # Выполнение команды
    result = subprocess.run(cp_command, shell=True, check=True, text=True)
    if result.returncode == 0:
        print("Файлы успешно скопированы и заменены.")
    else:
        print("Ошибка при копировании файлов.")
except subprocess.CalledProcessError as e:
    print(f"Ошибка при копировании файлов: {e}")

/opt/SQL_Tester/my_app/Тестируемые/'Ядыкин Алексей'
/opt/SQL_Tester/my_app/Тестируемые/Ядыкин\ Алексей