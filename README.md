# OTT Movie Recommendation System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API-black?style=for-the-badge&logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![SVD](https://img.shields.io/badge/SVD-Collaborative%20Filtering-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

**A collaborative filtering-based movie recommendation system with a Flask API and MySQL backend.**

[Overview](#-overview) · [Architecture](#️-architecture) · [Setup](#-setup) · [How It Works](#-how-it-works)

</div>

---

## Overview

A full-stack OTT recommendation engine that uses **SVD (Singular Value Decomposition)** to predict personalised movie ratings for users — served via a **Flask REST API** with a clean web UI.

The system loads real movie, user, and rating data into **MySQL**, trains a collaborative filtering model using the `Surprise` library, caches predictions, and serves them through API endpoints with a dashboard for stats and recommendations.

---

## Project Structure

```
ott-recommendation/
│
├── data/
│   ├── Movies.csv          # Movie metadata (title, genres, IMDB rating, etc.)
│   ├── Users.csv           # User IDs
│   └── ratings.csv         # User-movie ratings
│
├── sql/
│   └── create_tables.sql   # MySQL schema
│
├── src/
│   ├── app.py              # Flask API server
│   ├── db_config.py        # MySQL connection config
│   ├── load_data.py        # Loads CSV data into MySQL
│   ├── train_model.py      # Trains SVD model & caches predictions
│   ├── store_predictions.py# Stores predictions CSV into MySQL
│   └── recommend.py        # Query recommendations for a user
│
├── ui/
│   └── index.html          # Web dashboard
│
├── requirements.txt
└── README.md
```

---

## Architecture

```
CSV Data (Movies / Users / Ratings)
            ↓
     load_data.py
            ↓
       MySQL Database
       ┌────────────────────────┐
       │  users · movies        │
       │  ratings · predictions │
       └────────────────────────┘
            ↓
     train_model.py
     (SVD via Surprise)
            ↓
   predictions_cache.csv
            ↓
   store_predictions.py
            ↓
       MySQL predictions table
            ↓
       Flask API (app.py)
            ↓
       Web UI (index.html)
```

---

## How It Works

### 1. Data Loading
`load_data.py` reads the three CSV files and inserts them into MySQL — handling genre parsing, date formatting, and foreign key constraints cleanly.

### 2. Model Training
`train_model.py` fetches ratings from MySQL and trains an **SVD model** using the `Surprise` library:
- 50 latent factors, 30 epochs
- Learning rate: 0.005 | Regularisation: 0.02
- 3-fold cross-validation with RMSE and MAE reporting

Predictions are generated for every unseen (user, movie) pair and cached to `predictions_cache.csv`.

### 3. Storing Predictions
`store_predictions.py` reads the cached CSV and bulk-inserts predictions into the MySQL `predictions` table.

### 4. Serving Recommendations
`app.py` exposes REST endpoints that query the predictions table and return personalised movie recommendations ranked by predicted rating.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard |
| GET | `/api/users` | List all users |
| GET | `/api/movies` | List all movies (sorted by IMDB rating) |
| GET | `/api/recommend/<user_id>` | Top-N recommendations for a user |
| GET | `/api/stats` | Dashboard stats (users, movies, ratings, predictions) |
| POST | `/api/rate` | Submit a new rating |

**Example:**
```
GET /api/recommend/1?top_n=5
```

---

## Database Schema

```sql
users       → user_id
movies      → movie_id, title, genres, release_date, runtime, popularity, imdb_rating
ratings     → user_id, movie_id, rating, timestamp
predictions → user_id, movie_id, predicted_rating
```

---

## Setup

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

### 1. Clone the repo
```bash
git clone https://github.com/AmithaMahesh/ott-recommendation.git
cd ott-recommendation
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure MySQL
Edit `src/db_config.py` with your MySQL credentials:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD_HERE",
    "database": "ott"
}
```

### 4. Create the database
```bash
mysql -u root -p < sql/create_tables.sql
```

### 5. Load data
```bash
cd src
python load_data.py
```

### 6. Train the model
```bash
python train_model.py
```

### 7. Store predictions
```bash
python store_predictions.py
```

### 8. Run the server
```bash
python app.py
```

Visit **http://localhost:5000** to open the dashboard.

---

## Requirements

```
flask
flask-cors
mysql-connector-python
pandas
scikit-surprise
```

---

## Future Work

- User authentication and personalised login
- Real-time model retraining on new ratings
- Content-based filtering hybrid (genres, cast, director)
- Deployed cloud version
- Movie search and filter on the UI

---

## Tags

`Python` `Flask` `MySQL` `SVD` `Collaborative Filtering` `Recommendation System` `Machine Learning` `Surprise` `OTT` `REST API`
