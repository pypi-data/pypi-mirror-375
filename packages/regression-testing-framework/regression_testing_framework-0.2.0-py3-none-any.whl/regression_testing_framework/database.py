import sqlite3
from datetime import datetime

DB_FILE = "results.db"

def init_db():
    """Creates the database if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                config_name TEXT,
                command TEXT,
                success BOOLEAN,
                start_time TEXT,
                end_time TEXT,
                log_file TEXT,
                error_trace TEXT,
                failure TEXT
            )
        """)
        conn.commit()

def log_run(run_id: str, config_name: str, command: str, success: bool, start_time: datetime, end_time: datetime, log_file: str, error_trace: list = None, failure: str = None):
    """Logs a test run to the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO test_runs (run_id, config_name, command, success, start_time, end_time, log_file, error_trace, failure)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (run_id, config_name, command, success, start_time.isoformat(), end_time.isoformat(), log_file, "\n".join(error_trace) if error_trace else None, failure))
        conn.commit()

# Initialize DB on import
init_db()
