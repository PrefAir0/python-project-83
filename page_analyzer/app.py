import os
import psycopg
from datetime import date
from urllib.parse import urlparse
import validators
from flask import *
from dotenv import load_dotenv
import requests


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg.connect(os.environ.get('DATABASE_URL'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form.get('url', '')

    if not validators.url(url) or len(url) > 255:
        flash('Некорректный URL', 'danger')
        return render_template('index.html', url_input=url), 422

    parsed = urlparse(url)
    normalized_url = f"{parsed.scheme}://{parsed.netloc}"

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (normalized_url,))
            existing_url = cur.fetchone()

            if existing_url:
                flash('Страница уже существует', 'info')
                url_id = existing_url[0]
            else:
                cur.execute(
                    "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                    (normalized_url, date.today())
                )
                url_id = cur.fetchone()[0]
                conn.commit()
                flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=url_id))

@app.route('/urls')
def get_urls():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (urls.id)
        urls.id,
        urls.name,
        url_checks.created_at AS last_check_date,
        url_checks.status_code AS last_check_status
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        ORDER BY urls.id DESC, url_checks.id DESC
    """)
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('urls.html', urls=urls)

@app.route('/urls/<int:id>')
def show_url(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
    url = cur.fetchone()
    
    if not url:
        cur.close()
        conn.close()
        return "Сайт не найден", 404

    cur.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC", (id,))
    checks = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('url.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def add_check(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM urls WHERE id = %s", (id,))
    url_row = cur.fetchone()
    
    if not url_row:
        cur.close()
        conn.close()
        return "Страница не найдена", 404
        
    url_name = url_row[0]
    try:
        response = requests.get(url_name, timeout=5)

        response.raise_for_status()

        cur.execute(
            "INSERT INTO url_checks (url_id, status_code, created_at) VALUES (%s, %s, %s)",
            (id, response.status_code, date.today())
        )
        conn.commit()
        flash('Страница успешно проверена', 'success')
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    finally:
        cur.close()
        conn.close()
        
    return redirect(url_for('show_url', id=id))