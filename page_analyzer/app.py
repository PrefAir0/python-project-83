import os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
import psycopg
import requests

from . import database, parser, url_normalizer

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    return psycopg.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form.get('url', '')

    if not url_normalizer.is_valid(url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html', url_input=url), 422

    normalized_url = url_normalizer.normalize(url)

    with get_db_connection() as conn:
        existing_url = database.get_url_by_name(conn, normalized_url)

        if existing_url:
            flash('Страница уже существует', 'info')
            url_id = existing_url[0]
        else:
            url_id = database.add_url(conn, normalized_url)
            flash('Страница успешно добавлена', 'success')

    return redirect(url_for('show_url', id=url_id))


@app.route('/urls')
def get_urls():
    with get_db_connection() as conn:
        urls = database.get_all_urls(conn)
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>')
def show_url(id):
    with get_db_connection() as conn:
        url = database.get_url_by_id(conn, id)
        if not url:
            return "Сайт не найден", 404

        checks = database.get_checks_by_url_id(conn, id)

    return render_template('url.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def add_check(id):
    with get_db_connection() as conn:
        url_row = database.get_url_by_id(conn, id)
        if not url_row:
            return "Страница не найдена", 404

        url_name = url_row[1]

        try:
            response = requests.get(url_name, timeout=5)
            response.raise_for_status()

            h1, title, content = parser.parse_html(response.text)

            database.add_check(
                conn, id, response.status_code, h1, title, content
            )
            flash('Страница успешно проверена', 'success')

        except requests.RequestException:
            flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('show_url', id=id))
