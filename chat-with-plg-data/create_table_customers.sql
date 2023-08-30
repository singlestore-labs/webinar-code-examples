CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    created_at DATETIME,
    email VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(255),
    user_id VARCHAR(255),
    seg_message_id VARCHAR(255),
    seg_received_at DATETIME,
    seg_sent_at DATETIME,
    seg_timestamp DATETIME,
    embedding BLOB NOT NULL
);