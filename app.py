from flask import Flask, render_template
import pymysql
import os

app = Flask(__name__)

@app.route("/")
def index():
    try:
        conn = pymysql.connect(
            host="metro.proxy.rlwy.net",
            port=39083,
            user="root",
            password="CXJqQqOlYTACMQZPdSaNyvUeLtnfHVvH",
            database="railway",
            charset="utf8mb4"
        )
        cursor = conn.cursor()

        # 최근 로그 불러오기
        cursor.execute("SELECT id, message, created_at FROM wrist_log ORDER BY created_at DESC LIMIT 10")
        rows = cursor.fetchall()

        logs = []
        for row in rows:
            log = {
                "id": row[0],
                "message": row[1],
                "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S"),
                "status": "⚠️ 손목 꺾임 감지" if "1" in row[1] else "✅ 정상"
            }
            logs.append(log)

        # 시간대별 꺾임 횟수 통계
        cursor.execute("SELECT HOUR(created_at), COUNT(*) FROM wrist_log GROUP BY HOUR(created_at)")
        time_data = cursor.fetchall()
        labels = [f"{hour}시" for hour, _ in time_data]
        data = [count for _, count in time_data]

        cursor.close()
        conn.close()

        return render_template("index.html", logs=logs, labels=labels, data=data)

    except Exception as e:
        return f"❌ DB 연결 실패: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
