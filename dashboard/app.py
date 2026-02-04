from flask import Flask, render_template, jsonify
import psycopg2

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        "host=localhost dbname=socdb user=socuser password=socpass123"
    )

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def stats():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT threat_level, COUNT(*) FROM events GROUP BY threat_level"
            )
            data = dict(cur.fetchall())
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)
