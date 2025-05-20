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

        # 1. 최근 로그 10개 조회
        cursor.execute("""
            SELECT id, message, created_at 
            FROM wrist_log 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
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

        # 2. 최근 30일간 '1' 포함된 손목 꺾임 - 날짜+시간대별 집계
        cursor.execute("""
            SELECT DATE_FORMAT(created_at, '%m/%d %H시') AS datetime_label, COUNT(*) 
            FROM wrist_log 
            WHERE message LIKE '%1%' 
              AND created_at >= NOW() - INTERVAL 30 DAY
            GROUP BY datetime_label
            ORDER BY MIN(created_at)
        """)
        time_data = cursor.fetchall()
        labels = [label for label, _ in time_data]
        data = [count for _, count in time_data]

        cursor.close()
        conn.close()

        return render_template("index.html", logs=logs, labels=labels, data=data)

    except Exception as e:
        return f"❌ DB 연결 실패: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
