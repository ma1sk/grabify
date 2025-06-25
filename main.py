import sqlite3
import requests
from flask import Flask, request, render_template, redirect
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'grabify.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            timestamp TEXT,
            city TEXT,
            region TEXT,
            country TEXT,
            user_agent TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_geo(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,city,regionName,country")
        data = resp.json()
        if data.get("status") == "success":
            return data.get("city"), data.get("regionName"), data.get("country")
        else:
            return None, None, None
    except Exception:
        return None, None, None

def get_client_ip():
    # Check headers that may contain the real IP if behind a proxy
    if 'X-Forwarded-For' in request.headers:
        # Can be multiple IPs, take the first one
        ip = request.headers['X-Forwarded-For'].split(',')[0].strip()
    elif 'X-Real-IP' in request.headers:
        ip = request.headers['X-Real-IP']
    else:
        ip = request.remote_addr
    return ip

@app.route('/')
def index():
    redirect_url = 'https://youtube.com'  # Change to your redirect target

    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    city, region, country = get_geo(ip)
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO captures (ip, timestamp, city, region, country, user_agent) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ip, timestamp, city, region, country, user_agent))
    conn.commit()
    conn.close()

    return redirect(redirect_url)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT ip, timestamp, city, region, country, user_agent FROM captures ORDER BY id DESC')
    records = [
        {
            "ip": row[0],
            "timestamp": row[1],
            "city": row[2],
            "region": row[3],
            "country": row[4],
            "user_agent": row[5]
        } for row in c.fetchall()
    ]
    conn.close()
    return render_template('dashboard.html', records=records)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

