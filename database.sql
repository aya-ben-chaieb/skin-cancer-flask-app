CREATE DATABASE skin_cancer_db;
USE skin_cancer_db;

-- USERS TABLE (authentication)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(255)
);

-- PATIENTS TABLE (analysis history)
CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    result VARCHAR(20),
    probability FLOAT,
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DEFAULT ADMIN USER
INSERT INTO users (username, password)
VALUES ('admin', '1234');

-- Aya User
INSERT INTO users (username, password)
VALUES ('aya', '2003');