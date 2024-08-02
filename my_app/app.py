from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import pytz
import pandas as pd
import sqlite3
import os
import json
from flask import send_from_directory
import logging
from logging.handlers import RotatingFileHandler
from waitress import serve

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Получаем путь к директории, где находится текущий скрипт
base_dir = os.path.dirname(os.path.abspath(__file__))

# Составляем пути относительно директории скрипта
db_path = os.path.join(base_dir, 'your_database.db')
base_path = os.path.join(base_dir, r'Тестируемые')
etalon_dir = os.path.join(base_dir, 'ResultEtalon')
otps_file = os.path.join(base_dir, 'otps.txt')

# Подключение к базе данных SQLite
users = {
    'Admin_1': '123',
    'Admin_2': '321'
}

# Загружаем одноразовые пароли (OTP)
def load_otps(file):
    with open(file, 'r') as f:
        return [line.strip() for line in f]

def save_otps(otps, file):
    with open(file, 'w') as f:
        f.writelines([otp + '\n' for otp in otps])

otps = load_otps(otps_file)

# Функция для загрузки эталонных данных
def load_etalon_data():
    etalon_data = {}
    if not os.path.exists(etalon_dir):
        return etalon_data
    for task_file in os.listdir(etalon_dir):
        if task_file.startswith('Task_') and task_file.endswith('.json'):
            task_id = int(task_file.split('_')[1].split('.')[0])
            full_path = os.path.join(etalon_dir, task_file)
            with open(full_path, 'r', encoding='utf-8') as file:
                etalon_data[task_id] = json.load(file)
    return etalon_data

# Функция для сравнения результатов
def compare_results(user_result, etalon_result):
    if user_result is None or etalon_result is None:
        return False
    if len(user_result) != len(etalon_result):
        return False
    for user_row, etalon_row in zip(user_result, etalon_result):
        if user_row != etalon_row:
            return False
    return True

# Список вопросов
questions = [
    {
        "id": 1,
        "text": "Вывести все товары, в наименовании которых содержится 'самокат' (без учета регистра), и срок годности которых не превышает 7 суток.\n\nДанные на выходе:\n- наименование товара (as name)\n- срок годности (as shelf_life)"
    },
    {
        "id": 2,
        "text": "Посчитать количество работающих складов на дату 2024-06-11 по каждому городу. Вывести только те города, у которых количество складов более 50.\n\nДанные на выходе:\n- город (as city)\n- количество складов (as warehouse_count)"
    },
    {
        "id": 3,
        "text": "Посчитать среднее количество товаров (SKU) на 1 склад, которые продавались в июне 2020 года, и вывести данные в разрезе городов.\n\nДанные на выходе:\n- город (as city)\n- количество складов (as складов)\n- количество товаров с продажами на 1 склад (as товаров_на_1_склад)"
    },
    {
        "id": 4,
        "text": "Посчитать количество заказов и количество клиентов в разрезе месяцев за 2021 год по компании в целом и по каждому городу.\n\nДанные на выходе:\n- город/компания (as город)\n- месяц (as месяц)\n- количество заказов (as количество_заказов)\n- количество клиентов (as количество_клиентов)"
    },
    {
        "id": 5,
        "text": "Посчитать средний заказ в рублях по каждому складу за последние 14 дней от '2024-06-10'. Вывести в алфавитном порядке наименования только тех складов, где средний заказ выше, чем средний заказ по городу.\n\nДанные на выходе:\n- наименование склада (as warehouse_name)\n- город (as city)\n- средний заказ по складу (as avg_order_warehouse)\n- средний заказ по городу (as avg_order_city)"
    },
    {
        "id": 6,
        "text": "Рассчитать процент потерь (от суммы продаж соответствующей группы) и долю потерь в общей сумме потерь по компании в целом за последние 4 недели по каждой группе товаров 2 уровня, учитывая все статьи потерь. Для текущей даты использовать '2024-06-10'.\n\nДанные на выходе:\n- группа товаров 1 уровня (as group1)\n- группа товаров 2 уровня (as group2)\n- сумма продаж (as total_sales_amount)\n- сумма потерь (as total_loss_amount)\n- процент потерь от продаж (as pct_loss_from_sales)\n- доля потерь в общей сумме потерь (as loss_share)"
    },
    {
        "id": 7,
        "text": "Построить рейтинги товаров за май 2021 года по всем складам в Москве. Строим два рейтинга:\n- рейтинг по средней сумме продаж на один склад в рамках группы товаров 1 уровня\n- рейтинг по средней сумме потерь на один склад в рамках группы товаров 1 уровня\n\nВ итоге вывести топ-10 товаров по потерям и продажам в каждой группе и только там, где есть продажи и потери.\n\nДанные на выходе:\n- группа товаров 1 уровня (as group1)\n- наименование товара (as name)\n- сумма продаж на 1 склад (as сумма_продаж_на_1_склад)\n- рейтинг по продажам (as рейтинг_по_продажам)\n- сумма потерь на 1 склад (as сумма_потерь_на_1_склад)\n- рейтинг по потерям (as рейтинг_по_потерям)"
    }
]



@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            error_message = 'Неправильный логин или пароль'
            return render_template('admin_login.html', error=error_message)
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session:
        return redirect(url_for('admin_login'))

    etalon_data = load_etalon_data()
    test_results = {}

    for user_dir in os.listdir(base_path):
        user_path = os.path.join(base_path, user_dir)
        if os.path.isdir(user_path):
            creation_time = datetime.fromtimestamp(os.path.getctime(user_path))
            creation_date_str = creation_time.strftime('%Y-%m-%d %H:%M')
            results = {}
            total = 0
            for task_id in etalon_data:
                user_file = os.path.join(user_path, f'Task_{task_id}.json')
                if os.path.exists(user_file):
                    with open(user_file, 'r', encoding='utf-8') as file:
                        user_data = json.load(file)
                    match = compare_results(user_data["result"], etalon_data[task_id]["result"])
                    results[task_id] = match
                    total += int(match)  # Суммируем количество совпадений
                else:
                    results[task_id] = False

            # Загрузка существующих данных пользователей или создание новых, если нет
            user_data_file = os.path.join(user_path, 'user_data.json')
            if os.path.exists(user_data_file):
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                excel_scores = user_data.get('excel_scores', {f'Excel_{i}': 0 for i in range(1, 6)})
            else:
                excel_scores = {f'Excel_{i}': 0 for i in range(1, 6)}

            # Искать загруженные Excel-файлы
            excel_files = [f for f in os.listdir(user_path) if f.endswith('.xlsx')]

            total += sum(excel_scores.values())  # добавляем Excel результаты к итогу
            test_results[user_dir] = {
                'results': results,
                'total': total,
                'creation_date': creation_date_str,
                'excel_scores': excel_scores,
                'excel_files': excel_files
            }

    return render_template('admin_dashboard.html', test_results=test_results)


@app.route('/download/<user>/<filename>')
def download_file(user, filename):
    if 'user' not in session:
        return redirect(url_for('admin_login'))

    user_dir = os.path.join(base_path, user)
    return send_from_directory(directory=user_dir, path=filename, as_attachment=True)


@app.route('/admin/details')
def admin_details():
    if 'user' not in session:
        return redirect(url_for('admin_login'))

    user = request.args.get('user')
    task_id = request.args.get('task')
    etalon_data = load_etalon_data()

    user_file_path = os.path.join(base_path, user, f'Task_{task_id}.json')
    if os.path.exists(user_file_path):
        with open(user_file_path, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
    else:
        user_data = {"query": "Файл не найден", "result": [], "error": None}

    etalon_task_data = etalon_data.get(int(task_id), {"query": "Эталон не найден", "result": [], "error": None})

    user_results = user_data.get('result', []) if user_data.get('result') is not None else []
    etalon_results = etalon_task_data.get('result', []) if etalon_task_data.get('result') is not None else []

    return render_template('admin_detail.html', user=user, task_id=task_id, user_data=user_data, etalon_data=etalon_task_data, user_results=user_results, etalon_results=etalon_results)



@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        fio = request.form['fio']
        otp = request.form['otp']

        if otp in otps:
            session['fio'] = fio
            session['start_time'] = datetime.now(pytz.utc)
            session['attempts'] = {q['id']: 0 for q in questions}
            session['completed_questions'] = []
            otps.remove(otp)
            save_otps(otps, otps_file)

            return render_template('login.html', show_instructions=True)
        else:
            error_message = 'Неверный одноразовый пароль'

    return render_template('login.html', error=error_message)


@app.route('/question/<int:id>')
def question(id):
    if 'fio' not in session or 'start_time' not in session:
        return redirect(url_for('login'))

    elapsed_time = datetime.now(pytz.utc) - session['start_time']
    remaining_time = timedelta(minutes=90) - elapsed_time  # 90 минут вместо 40
    if remaining_time.total_seconds() <= 0:
        return redirect(url_for('finish_test'))

    completed_questions = session.get('completed_questions', [])
    completed_questions = [str(q) for q in completed_questions]  # Приведение к строкам

    if str(id) in completed_questions:
        remaining_questions = [q for q in questions if str(q['id']) not in completed_questions]
        return render_template('completed.html', completed_question_id=id,
                               remaining_questions=remaining_questions)

    question = next((q for q in questions if q['id'] == id), None)
    if not question:
        return redirect(url_for('finish_test'))

    session['current_question'] = id
    remaining_time_str = str(remaining_time).split('.')[0]
    attempts = session['attempts'].get(id, 0)

    return render_template('index.html', question=question, remaining_time_str=remaining_time_str,
                           attempts=attempts, remaining_time=remaining_time, result='',
                           completed_questions=completed_questions)

def is_ddl_query(query):
    ddl_keywords = ['CREATE', 'ALTER', 'DROP', 'TRUNCATE', 'RENAME', 'COMMENT', 'GRANT', 'REVOKE']
    for keyword in ddl_keywords:
        if keyword in query.upper():
            return True
    return False
@app.route('/execute_sql', methods=['POST'])
def execute_sql():
    if 'fio' not in session or 'start_time' not in session:
        return redirect(url_for('login'))

    elapsed_time = datetime.now(pytz.utc) - session['start_time']
    remaining_time = timedelta(minutes=90) - elapsed_time  # 90 минут вместо 40
    if remaining_time.total_seconds() <= 0:
        return jsonify({'error': 'Время вышло. Пожалуйста, завершите ваши действия.'})

    query = request.form.get('query')
    if is_ddl_query(query):
        return jsonify({'error': 'Выполнение DDL-запросов запрещено.'}), 400

    question_id = session.get('current_question')
    if question_id not in session['attempts']:
        session['attempts'][question_id] = 0
    session['attempts'][question_id] += 1

    if session['attempts'][question_id] > 5:
        return jsonify({'error': f'Превышено количество попыток для задания {question_id}'}), 400

    try:
        conn = sqlite3.connect(db_path)
        result_data = pd.read_sql_query(query, conn)
        conn.close()

        result_html = result_data.to_html(classes='table table-striped', index=False)

        return jsonify({'result': result_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/final_submit', methods=['POST'])
def final_submit():
    if 'fio' not in session or 'start_time' not in session:
        return jsonify({'error': 'Сессия истекла, пожалуйста, войдите снова.'})

    elapsed_time = datetime.now(pytz.utc) - session['start_time']
    remaining_time = timedelta(minutes=90) - elapsed_time
    if remaining_time.total_seconds() <= 0:
        return jsonify({'error': 'Время вышло. Пожалуйста, завершите ваши действия.'})

    query = request.form.get('query', '')
    question_id = session.get('current_question')
    fio = session.get('fio')

    user_dir = os.path.join(base_path, fio)
    os.makedirs(user_dir, exist_ok=True)
    json_filename = os.path.join(user_dir, f'Task_{question_id}.json')

    result_json = {
        "query": query,
        "result": None,
        "error": None
    }

    if query.strip():
        try:
            conn = sqlite3.connect(db_path)
            result = pd.read_sql_query(query, conn)
            conn.close()
            result_json["result"] = result.to_dict(orient='records')
        except Exception as e:
            result_json["error"] = str(e)

    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=4)

    question_id_str = str(question_id)
    if question_id_str not in session.get('completed_questions', []):
        session['completed_questions'].append(question_id_str)
    session['attempts'][question_id_str] = 5

    next_question_id = next(
        (q['id'] for q in questions if str(q['id']) not in session.get('completed_questions', [])), None)

    if next_question_id is None:
        return jsonify({'next_url': url_for('finish_test')})

    session['current_question'] = next_question_id

    return jsonify({'next_url': url_for('question', id=next_question_id)})


@app.route('/upload_excel/<user>', methods=['POST'])
def upload_excel(user):
    if 'user' not in session:
        return redirect(url_for('admin_login'))

    user_dir = os.path.join(base_path, user)
    os.makedirs(user_dir, exist_ok=True)

    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    file.save(os.path.join(user_dir, file.filename))
    return redirect(url_for('admin_dashboard'))


@app.route('/update_excel_score/<user>/<task_id>', methods=['POST'])
def update_excel_score(user, task_id):
    if 'user' not in session:
        return redirect(url_for('admin_login'))

    try:
        score = float(request.form['score'])
    except ValueError:
        return redirect(
            url_for('admin_dashboard'))  # Если что-то не так с преобразованием, отправить обратно на дашборд

    # Загрузка существующих данных пользователей или создание новых, если их нет
    user_dir = os.path.join(base_path, user)
    os.makedirs(user_dir, exist_ok=True)

    user_data_file = os.path.join(user_dir, 'user_data.json')
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    else:
        user_data = {'excel_scores': {f'Excel_{i}': 0 for i in range(1, 6)}}

    # Обновление оценки для соответствующего задания Excel
    user_data['excel_scores'][task_id] = score

    # Сохранение обратно в файл
    with open(user_data_file, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

    return redirect(url_for('admin_dashboard'))


@app.route('/finish_test')
def finish_test():
    session.clear()
    return "Тестирование завершено. Спасибо за участие!"

@app.route('/completed')
def completed():
    completed_question_id = request.args.get('completed_question_id')
    remaining_questions = [q for q in questions if str(q['id']) not in session.get('completed_questions')]

    return render_template('completed.html', completed_question_id=completed_question_id,
                           remaining_questions=remaining_questions)

if __name__ == '__main__':
    print("Server is running on http://2.59.43.100:8000")
    serve(app, host='0.0.0.0', port=8000)
