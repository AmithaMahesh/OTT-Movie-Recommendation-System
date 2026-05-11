CREATE DATABASE ott;
USE ott;

CREATE TABLE users (
    user_id INT PRIMARY KEY
);

CREATE TABLE movies (
    movie_id INT PRIMARY KEY,
    title VARCHAR(255),
    genres VARCHAR(255),
    release_date DATE,
    runtime FLOAT,
    popularity FLOAT,
    imdb_rating FLOAT
);

CREATE TABLE ratings (
    user_id INT,
    movie_id INT,
    rating FLOAT,
    timestamp BIGINT,
    PRIMARY KEY (user_id, movie_id)
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);

CREATE TABLE predictions (
    user_id INT,
    movie_id INT,
    predicted_rating FLOAT,
    PRIMARY KEY (user_id, movie_id)
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);