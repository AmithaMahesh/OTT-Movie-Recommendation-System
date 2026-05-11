# src/app.py
# Flask API — serves the UI and recommendation endpoints

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db_config import DB_CONFIG

# Build absolute path to ui/ folder regardless of where script is run from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")

app = Flask(__name__, static_folder=UI_DIR, static_url_path="")
CORS(app)

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ── Serve UI ──────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(UI_DIR, "index.html")

# ── Get all users ─────────────────────────────────────────
@app.route("/api/users")
def get_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id FROM users ORDER BY user_id")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

# ── Get all movies ────────────────────────────────────────
@app.route("/api/movies")
def get_movies():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies ORDER BY imdb_rating DESC")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(movies)

# ── Get recommendations for a user ───────────────────────
@app.route("/api/recommend/<int:user_id>")
def recommend(user_id):
    top_n = int(request.args.get("top_n", 5))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get user info
    cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    # Get recommendations
    cursor.execute("""
        SELECT m.movie_id, m.title, m.genres, m.imdb_rating,
               m.popularity, m.runtime, p.predicted_rating
        FROM predictions p
        JOIN movies m ON p.movie_id = m.movie_id
        WHERE p.user_id = %s
        ORDER BY p.predicted_rating DESC
        LIMIT %s
    """, (user_id, top_n))
    recs = cursor.fetchall()

    # Get movies the user has already rated
    cursor.execute("""
        SELECT m.title, r.rating
        FROM ratings r
        JOIN movies m ON r.movie_id = m.movie_id
        WHERE r.user_id = %s
        ORDER BY r.rating DESC
    """, (user_id,))
    rated = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "user": user,
        "recommendations": recs,
        "rated_movies": rated
    })

# ── Stats for dashboard ───────────────────────────────────
@app.route("/api/stats")
def stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM movies")
    total_movies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ratings")
    total_ratings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(rating) FROM ratings")
    avg_rating = round(cursor.fetchone()[0] or 0, 2)

    cursor.close()
    conn.close()

    return jsonify({
        "total_users": total_users,
        "total_movies": total_movies,
        "total_ratings": total_ratings,
        "total_predictions": total_predictions,
        "avg_rating": avg_rating
    })

# ── Add a rating ──────────────────────────────────────────
@app.route("/api/rate", methods=["POST"])
def add_rating():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO ratings (user_id, movie_id, rating, timestamp)
            VALUES (%s, %s, %s, UNIX_TIMESTAMP())
            ON DUPLICATE KEY UPDATE rating = VALUES(rating)
        """, (data["user_id"], data["movie_id"], data["rating"]))
        conn.commit()
        result = {"success": True, "message": "Rating saved!"}
    except Exception as e:
        result = {"success": False, "message": str(e)}
    cursor.close()
    conn.close()
    return jsonify(result)

if __name__ == "__main__":
    print("🚀 OTT Recommendation Server running at http://localhost:5000")
    app.run(debug=True, port=5000)