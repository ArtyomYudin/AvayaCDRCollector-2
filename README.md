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
3. Create DB table (example SQL provided in README).
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

## Notes & Assumptions
- The original Node app expected the CDR record fields separated by spaces and used the end time + duration to compute start time. This implementation follows the same logic.
- The server is resilient to malformed lines (it logs and ignores them).
