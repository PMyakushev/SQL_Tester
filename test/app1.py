from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import pandasql as psql
from datetime import datetime, timedelta
import pytz
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


# Загрузка одноразовых паролей
def load_otps(file):
    with open(file, 'r') as f:
        return [line.strip() for line in f]


def save_otps(otps, file='otps.txt'):
    with open(file, 'w') as f:
        f.writelines([otp + '\n' for otp in otps])


otps = load_otps('otps.txt')

# Список вопросов
questions = [
    {
        "id": 1,
        "text": "Задание №1\n\nВывести все товары, в наименовании которых содержится «самокат» (без учета регистра), и срок годности которых не превышает 7 суток.\n\nДанные на выходе – наименование товара, срок годности"
    },
    {
        "id": 2,
        "text": "Задание №2\n\nПосчитать количество работающих складов на текущую дату (2024-06-11) по каждому городу. Вывести только те города, у которых количество складов более 50.\n\nДанные на выходе - город, количество складов"
    },
    {
        "id": 3,
        "text": "Задание №3\n\nПосчитать среднее количество товаров (SKU) на 1 склад, которые продавались в июне 2020 года, данные вывести в разрезе городов.\n\nДанные на выходе - город, количество складов, количество товаров с продажами на 1 склад"
    },
    {
        "id": 4,
        "text": "Задание №4\n\nПосчитать количество заказов и количество клиентов в разрезе месяцев за 2021 год по компании в целом и по каждому из городов.\n\nДанные на выходе – город/компания, месяц, количество заказов, количество клиентов"
    },
    {
        "id": 5,
        "text": "Задание №5\n\nПосчитать средний заказ в рублях по каждому складу за последние 14 дней, при этом вывести в алфавитном порядке наименования только тех складов, где средний заказ выше, чем средний заказ по городу.\n\nДанные на выходе – наименование склада, город, средний заказ по складу, средний заказ по городу"
    },
    {
        "id": 6,
        "text": "Задание №6\n\nРассчитать % потерь (от суммы продаж соответствующей группы) и долю потерь в общей сумме потерь по компании в целом за последние 4 недели по каждой группе товаров 2 уровня (учитывая все статьи потерь).\n\nДанные на выходе – группа товаров 1 уровня, группа товаров 2 уровня, % потерь от продаж, доля потерь"
    },
    {
        "id": 7,
        "text": "Задание №7\n\nПостроить рейтинги товаров за май 2021 года по всем складам в Москве. Строим 2 рейтинга - рейтинг по средней сумме продаж на 1 склад в рамках группы товаров 1 уровня и рейтинг средней по сумме потерь на 1 склад в рамках группы товаров 1 уровня. В итоге выводим топ-10 товаров по потерям и продажам в каждой группе.\n\nДанные на выходе – группа товаров 1 уровня, наименование товара, сумма продаж на 1 склад, рейтинг по продажам, сумма потерь на 1 склад, рейтинг по потерям"
    }
]

# Проверка, что список вопросов не пустой
if not questions:
    raise ValueError("Список вопросов пуст. Добавьте вопросы в список.")


# Функция для загрузки данных из CSV в DataFrame
def load_data():
    base_path = 'data/'
    files = {
        'warehouses': 'WAREHOUSES.csv',
        'products': 'PRODUCTS.csv',
        'orders': 'ORDERS.csv',
        'order_line': 'ORDER_LINE.csv',
        'lost': 'LOST.csv'
    }

    data = {name: pd.read_csv(f"{base_path}{filename}") for name, filename in files.items()}
    return data


data = load_data()
globals().update(data)  # Добавляем DataFrame в глобальную область видимости


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        fio = request.form['fio']
        otp = request.form['otp']

        # Проверка одноразовых паролей
        if otp in otps:
            session['fio'] = fio
            session['start_time'] = datetime.now(pytz.utc)
            session['attempts'] = {q['id']: 0 for q in questions}
            session['used_otp'] = otp
            session['completed_questions'] = []
            otps.remove(otp)
            save_otps(otps)
            return redirect(url_for('question', id=1))
        else:
            error = 'Неправильный одноразовый пароль'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/question/<int:id>', methods=['GET'])
def question(id):
    if 'fio' not in session or 'start_time' not in session:
        return redirect(url_for('login'))

    elapsed_time = datetime.now(pytz.utc) - session['start_time']
    remaining_time = timedelta(minutes=40) - elapsed_time
    if remaining_time.total_seconds() <= 0:
        return redirect(url_for('login'))

    session['current_question'] = id
    question = questions[(id - 1) % len(questions)]
    remaining_time_str = str(remaining_time).split('.')[0]  # Отображаем оставшееся время в формате чч:мм:сс
    attempts = session['attempts'].get(id, 0)

    # Передача remaining_time.total_seconds() для использования в JavaScript
    return render_template('index.html', question=question, remaining_time=remaining_time.total_seconds(),
                           remaining_time_str=remaining_time_str, attempts=attempts)

@app.route('/execute_sql', methods=['POST'])
def execute_sql():
    if 'fio' not in session or 'start_time' not in session:
        return redirect(url_for('login'))

    elapsed_time = datetime.now(pytz.utc) - session['start_time']
    if elapsed_time > timedelta(minutes=40):
        return redirect(url_for('login'))

    query = request.form.get('query')
    question_id = session.get('current_question')
    if question_id not in session['attempts']:
        session['attempts'][question_id] = 0
    session['attempts'][question_id] += 1

    # Ограничение на 5 попыток
    if session['attempts'][question_id] > 5:
        return f'<pre>Error: Превышено количество попыток для задания {question_id}</pre>'

    try:
        # Выполнение SQL-запроса к DataFrame с использованием pandasql
        result = psql.sqldf(query, globals())

        return result.to_html(classes='table table-striped')
    except Exception as e:
        return f'<pre>Error: {str(e)}</pre>'

@app.route('/final_submit', methods=['POST'])
def final_submit():
    if 'fio' not in session or 'start_time' not in session:
        return redirect(url_for('login'))

    query = request.form.get('query')
    question_id = session['current_question']

    try:
        # Проверка SQL-запроса и сохранение результата
        result = psql.sqldf(query, globals())
        fio = session['fio']

        # Создание CSV файла с ФИО и запись результата
        filename = f'results_{fio}.csv'
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([fio, question_id, query, datetime.now(), result.to_html(classes='table table-striped')])

        # Добавление текущего вопроса в список завершённых вопросов
        session['completed_questions'].append(question_id)

        # Если это было 7-е нажатие на "Итоговая проверка", завершаем тест.
        if len(session['completed_questions']) >= 7:
            return redirect(url_for('finish_test'))

        # Удаление текущего вопроса из списка вопросов
        session['attempts'][question_id] = 5  # Максимальное число попыток на этот вопрос

        flash("Ваш код был записан. Переходите к следующему заданию.")
        next_question_id = next((q['id'] for q in questions if q['id'] not in session['completed_questions']), None)
        if next_question_id:
            return redirect(url_for('question', id=next_question_id))
        else:
            return redirect(url_for('finish_test'))
    except Exception as e:
        return f'<pre>Error: {str(e)}</pre>'

@app.route('/finish_test', methods=['GET'])
def finish_test():
    if 'fio' in session:
        session.clear()
    return render_template('finish.html')

if __name__ == '__main__':
    app.run(debug=True)




