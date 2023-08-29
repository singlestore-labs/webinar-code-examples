CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    event VARCHAR(255),
    seg_message_id VARCHAR(255),
    seg_original_timestamp DATETIME,
    seg_received_at DATETIME,
    seg_sent_at DATETIME,
    seg_timestamp DATETIME,
    user_id VARCHAR(255)
);