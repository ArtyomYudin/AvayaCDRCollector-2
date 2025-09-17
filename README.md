# Avaya CDR Collector (Python Async + PostgreSQL)

This project is a rewrite of the Node.js Avaya CDR Collector into Python 3.10+
using async IO, PostgreSQL, SQLAlchemy (async), and standard logging.

## Features
- Async TCP server accepting Avaya CDR lines
- Parses CDR line into start time, duration, calling number, called number, call code
- Inserts records into PostgreSQL using SQLAlchemy (async) and asyncpg
- Config via environment variables
- Uses Python `logging` (module `logger`) for logs

## Quick start (example)
1. Create a Python virtual environment (Python 3.10+ recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create PostgreSQL database and user, then set environment variables (see `.env.example`):
   ```bash
   export DB_HOST=127.0.0.1
   export DB_PORT=5432
   export DB_NAME=itsupport
   export DB_USER=avaya
   export DB_PASSWORD=secret
   export NET_SOCKET_ADDR=0.0.0.0
   export NET_SOCKET_PORT=9000
   ```
3. Create DB table (example SQL provided below).
4. Run the server:
   ```bash
   python -m app.main
   ```

## Files
- `app/main.py` — async TCP server entrypoint
- `app/parser.py` — parse incoming CDR line
- `app/db.py` — async SQLAlchemy engine and helper
- `app/models.py` — ORM model for `avaya_cdr`
- `app/logger.py` — logging configuration
- `requirements.txt` — Python dependencies
- `LICENSE` — MIT license
- `.env` — environment variables

## Input / Output format

The server receives Avaya CDR lines over TCP.  
Each line is space-separated and contains date, time, duration, and numbers.

### Example input line:
```
170925 1547 00252                    2434 0                2432
```

### Parsed fields:
- `170925` → call end date in **DDMMYY** → `2025-09-17`
- `1547`   → call end time in **HHMM** → `15:47:00`
- `00252`  → call duration:
  - `0` hours  
  - `02` minutes  
  - `52` seconds  
  = `172` seconds
- `2434`   → called number (`called_number`)
- `0`      → call code (`call_code`)
- `2432`   → calling number (`calling_number`)

### Stored in database (PostgreSQL table `avaya_cdr`):
| Field            | Value                  |
|------------------|------------------------|
| `date`           | `2025-09-17 15:44:08`  |
| `duration`       | `172`                  |
| `calling_number` | `2432`                 |
| `called_number`  | `2434`                 |
| `call_code`      | `0`                    |

> **Note**: start time is calculated as `end_time - duration`.

## Database schema (PostgreSQL)

```sql
CREATE TABLE IF NOT EXISTS avaya_cdr (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL,
    calling_number VARCHAR(50),
    called_number VARCHAR(50),
    call_code VARCHAR(10)
);
```

## Notes & Assumptions
- The original Node app expected the CDR record fields separated by spaces and used the end time + duration to compute start time. This implementation follows the same logic.
- The server is resilient to malformed lines (it logs and ignores them).
