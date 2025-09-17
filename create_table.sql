-- PostgreSQL table for avaya_cdr (example)
CREATE TABLE IF NOT EXISTS avaya_cdr (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL,
    calling_number VARCHAR(64),
    called_number VARCHAR(64),
    call_code VARCHAR(64)
);
