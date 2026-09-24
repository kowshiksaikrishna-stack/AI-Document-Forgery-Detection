CREATE DATABASE IF NOT EXISTS ai_document_screening;

USE ai_document_screening;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    document_type ENUM(
        'Aadhaar Card',
        'PAN Card',
        'Passport',
        'Voter ID'
    ) NOT NULL,

    document_hash VARCHAR(64) NOT NULL,
    ocr_status VARCHAR(50),
    face_status VARCHAR(50),
    forgery_score DECIMAL(5,2),
    risk_score DECIMAL(5,2),
    result VARCHAR(50),
    blockchain_tx VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);