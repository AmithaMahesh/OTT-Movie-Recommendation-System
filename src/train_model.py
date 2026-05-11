# src/train_model.py
# Fetches ratings from MySQL, trains SVD model, generates predictions

import pickle
import mysql.connector
import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate
from db_config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_ratings():
    conn = get_connection()
    df = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", conn)
    conn.close()
    print(f"📊 Fetched {len(df)} ratings from MySQL.")
    return df

def fetch_all_movie_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id FROM movies")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return ids

def train_and_predict():
    df = fetch_ratings()
    all_movie_ids = fetch_all_movie_ids()
    all_user_ids = df["user_id"].unique().tolist()

    # Prepare Surprise dataset
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], reader)

    # Train SVD
    print("🤖 Training SVD model...")
    model = SVD(n_factors=50, n_epochs=30, lr_all=0.005, reg_all=0.02)
    trainset = data.build_full_trainset()
    model.fit(trainset)

    # Cross-validate for reporting
    cv_results = cross_validate(model, data, measures=["RMSE", "MAE"], cv=3, verbose=False)
    rmse = cv_results["test_rmse"].mean()
    mae  = cv_results["test_mae"].mean()
    print(f"📈 Model RMSE: {rmse:.4f} | MAE: {mae:.4f}")

    # Generate predictions for every (user, movie) pair
    print("🔮 Generating predictions for all user-movie pairs...")
    predictions = []
    rated_pairs = set(zip(df["user_id"], df["movie_id"]))

    for uid in all_user_ids:
        for mid in all_movie_ids:
            if (uid, mid) not in rated_pairs:
                pred = model.predict(uid, mid)
                predictions.append((uid, mid, round(pred.est, 4)))

    # Save model + predictions to disk
    with open("src/svd_model.pkl", "wb") as f:
        pickle.dump(model, f)

    pd.DataFrame(predictions, columns=["user_id", "movie_id", "predicted_rating"])\
      .to_csv("src/predictions_cache.csv", index=False)

    print(f"✅ {len(predictions)} predictions generated and cached.")
    print("💾 Model saved as src/svd_model.pkl")
    return predictions

if __name__ == "__main__":
    train_and_predict()