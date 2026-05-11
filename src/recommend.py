# src/recommend.py
# Queries MySQL to get top N recommendations for a given user

import mysql.connector
from db_config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def recommend(user_id: int, top_n: int = 5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT m.title, m.genres, m.imdb_rating, p.predicted_rating
        FROM predictions p
        JOIN movies m ON p.movie_id = m.movie_id
        WHERE p.user_id = %s
        ORDER BY p.predicted_rating DESC
        LIMIT %s
    """
    cursor.execute(query, (user_id, top_n))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

if __name__ == "__main__":
    uid = 1
    recs = recommend(uid, top_n=5)

    print(f"\n🎬 Top 5 Recommendations for User {uid}:")
    print("─" * 50)
    for i, r in enumerate(recs, 1):
        print(f"{i}. {r['title']}")
        print(f"   Genre: {r['genres']}")
        print(f"   IMDB: {r['imdb_rating']} ⭐  |  Predicted: {r['predicted_rating']:.2f} ⭐")
    print("─" * 50)