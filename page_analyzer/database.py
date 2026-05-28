from datetime import date

def get_url_by_name(conn, name):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s", (name,))
        return cur.fetchone()

def add_url(conn, name):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
            (name, date.today())
        )
        url_id = cur.fetchone()[0]
        conn.commit()
        return url_id

def get_all_urls(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT urls.id, urls.name, 
                latest_checks.created_at AS last_check_date, 
                latest_checks.status_code AS last_check_status
            FROM urls
            LEFT JOIN (
                SELECT DISTINCT ON (url_id) url_id, created_at, status_code
                FROM url_checks
                ORDER BY url_id, id DESC
            ) AS latest_checks ON urls.id = latest_checks.url_id
            ORDER BY urls.id DESC
        """)
        return cur.fetchall()

def get_url_by_id(conn, id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
        return cur.fetchone()

def get_checks_by_url_id(conn, id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC", 
            (id,)
        )
        return cur.fetchall()

def add_check(conn, url_id, status_code, h1, title, description):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO url_checks 
            (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (url_id, status_code, h1, title, description, date.today()))
        conn.commit()