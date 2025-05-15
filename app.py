from flask import Flask, render_template
import pymysql
import os

app = Flask(__name__)

@app.route("/")
def index():
    try:
        conn = pymysql.connect(
            host="metro.proxy.rlwy.net",
            port=39083,  # 포트는 너 DB에 맞게
            user="root",
            password="CXJqQqOlYTACMQZPdSaNyvUeLtnfHVvH",
            database="railway",
            charset="utf8mb4"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wrist_log ORDER BY created_at DESC LIMIT 10")
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("index.html", logs=logs)
    except Exception as e:
        return f"❌ DB 연결 실패: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
