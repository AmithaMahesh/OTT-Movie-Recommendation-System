# src/store_predictions.py
# Reads cached predictions CSV and stores them into MySQL predictions table

import pandas as pd
import mysql.connector
from db_config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def store_predictions():
    df = pd.read_csv("src/predictions_cache.csv")
    conn = get_connection()
    cursor = conn.cursor()

    # Clear old predictions
    cursor.execute("DELETE FROM predictions")

    inserted = 0
    for _, row in df.iterrows():
        cursor.execute(
            """INSERT INTO predictions (user_id, movie_id, predicted_rating)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE predicted_rating = VALUES(predicted_rating)""",
            (int(row["user_id"]), int(row["movie_id"]), float(row["predicted_rating"]))
        )
        inserted += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Stored {inserted} predictions into MySQL.")

if __name__ == "__main__":
    print("Storing predictions into MySQL...")
    store_predictions()
    print("Done")