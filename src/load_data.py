# src/load_data.py
# Reads CSV files and loads them into MySQL

import re
import pandas as pd
import mysql.connector
from datetime import datetime
from db_config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def load_users():
    df = pd.read_csv("data/Users.csv")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ratings")   # clear dependents first
    cursor.execute("DELETE FROM predictions")
    cursor.execute("DELETE FROM users")
    for _, row in df.iterrows():
        cursor.execute(
            "INSERT INTO users (user_id) VALUES (%s)",
            (int(row["user_id"]),)
        )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loaded {len(df)} users into MySQL.")

def parse_genres(genres_str):
    """Extract just the genre names from the list-of-dicts string."""
    names = re.findall(r"'name':\s*'([^']+)'", str(genres_str))
    return ", ".join(names) if names else str(genres_str)

def load_movies():
    df = pd.read_csv("data/Movies.csv")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies")
    for _, row in df.iterrows():
        # Convert DD-MM-YYYY -> YYYY-MM-DD for MySQL
        try:
            release_date = datetime.strptime(str(row["release_date"]), "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            try:
                release_date = datetime.strptime(str(row["release_date"]), "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                release_date = None

        genres_clean = parse_genres(row["genres"])

        cursor.execute(
            """INSERT INTO movies (movie_id, title, genres, release_date, runtime, popularity, imdb_rating)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (int(row["movie_id"]), row["title"], genres_clean,
             release_date, float(row["runtime"]),
             float(row["popularity"]), float(row["imdb_rating"]))
        )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loaded {len(df)} movies into MySQL.")

def load_ratings():
    df = pd.read_csv("data/ratings.csv")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ratings")

    # Fetch valid IDs already in DB to avoid FK violations
    cursor.execute("SELECT movie_id FROM movies")
    valid_movies = {row[0] for row in cursor.fetchall()}
    cursor.execute("SELECT user_id FROM users")
    valid_users = {row[0] for row in cursor.fetchall()}

    inserted, skipped = 0, 0
    for _, row in df.iterrows():
        uid, mid = int(row["user_id"]), int(row["movie_id"])
        if uid not in valid_users or mid not in valid_movies:
            skipped += 1
            continue
        cursor.execute(
            "INSERT INTO ratings (user_id, movie_id, rating, timestamp) VALUES (%s, %s, %s, %s)",
            (uid, mid, float(row["rating"]), int(row["timestamp"]))
        )
        inserted += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loaded {inserted} ratings into MySQL. (Skipped {skipped} with missing user/movie)")

if __name__ == "__main__":
    print("Loading data into MySQL...")
    load_users()
    load_movies()
    load_ratings()
    print("\nAll data loaded successfully!")