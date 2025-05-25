from flask import Flask, render_template, jsonify
import pymysql
import 

app = Flask(__name__)

# 메인 페이지
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

        # 최근 로그 10개 조회
        cursor.execute("""
            SELECT id, message, created_at 
            FROM wrist_log 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        logs = [{
            "id": row[0],
            "message": row[1],
            "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S"),
            "status": "⚠️ 손목 꺾임 감지" if "1" in row[1] else "✅ 정상"
        } for row in rows]

        # 시간대별 꺾임 분석 (최근 30일)
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

        # 꺾임 총합
        cursor.execute("""
            SELECT COUNT(*) 
            FROM wrist_log 
            WHERE message LIKE '%1%' 
              AND created_at >= NOW() - INTERVAL 30 DAY
        """)
        total_bends = cursor.fetchone()[0]

        # 꺾임 발생한 날짜 수
        cursor.execute("""
            SELECT COUNT(DISTINCT DATE(created_at)) 
            FROM wrist_log 
            WHERE message LIKE '%1%' 
              AND created_at >= NOW() - INTERVAL 30 DAY
        """)
        bend_days = cursor.fetchone()[0]

        # 평균 꺾임
        avg_bends = round(total_bends / bend_days, 2) if bend_days > 0 else 0

        cursor.close()
        conn.close()

        return render_template(
            "index.html",
            logs=logs,
            labels=labels,
            data=data,
            total_bends=total_bends,
            bend_days=bend_days,
            avg_bends=avg_bends
        )

    except Exception as e:
        return f"❌ DB 연결 실패: {e}"


# 실시간 로그 조회용 API
@app.route("/api/logs")
def get_latest_logs():
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

        cursor.execute("""
            SELECT id, message, created_at 
            FROM wrist_log 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        logs = [{
            "id": row[0],
            "message": row[1],
            "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S"),
            "status": "⚠️ 손목 꺾임 감지" if "1" in row[1] else "✅ 정상"
        } for row in rows]

        return jsonify({"logs": logs})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
