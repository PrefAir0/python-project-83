from flask import Flask, request, render_template, flash, redirect, url_for
import requests
from . import database, parser, url_normalizer
app = Flask(__name__)

@app.route('/urls', methods=['POST'])
def urls_post():
    raw_url = request.form.get('url')
    
    if not url_normalizer.is_valid(raw_url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422
        
    normalized_url = url_normalizer.normalize(raw_url)

    conn = database.get_connection(app.config['DATABASE_URL'])
    existing_url = database.get_url_by_name(conn, normalized_url)
    
    if existing_url:
        flash('Страница уже существует', 'info')
        return redirect(url_for('url_show', id=existing_url['id']))
        
    url_id = database.add_url(conn, normalized_url)
    conn.close()
    
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_show', id=url_id))