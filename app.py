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
        cursor.execute("SELECT id, message, created_at FROM wrist_log ORDER BY created_at DESC LIMIT 10")
        rows = cursor.fetchall()

        # 컬럼별로 파싱된 리스트 만들기
        logs = []
        for row in rows:
            log = {
                "id": row[0],
                "message": row[1],
                "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S"),
                "status": "⚠️ 손목 꺾임 감지" if "1" in row[1] else "✅ 정상"
            }
            logs.append(log)

        cursor.close()
        conn.close()

        return render_template("index.html", logs=logs)
    except Exception as e:
        return f"❌ DB 연결 실패: {e}"
