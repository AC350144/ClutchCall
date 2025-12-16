import sqlite3
import threading
from datetime import datetime
import os
import logging

from clipboard_crypto import clipboard_crypto, SecureMemory, SecureString

logger = logging.getLogger(__name__)


class ClipboardDB:
    def __init__(self, db_path="clipboard_history.db"):
        self.db_path = os.path.abspath(db_path)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            self.db_path,
            timeout=30,
            check_same_thread=False
        )
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self.init_db()

    def init_db(self):
        with self._lock:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            self._conn.commit()

    def add_entry(self, content: str):
        timestamp = datetime.now().isoformat()
        with SecureString(content.strip()) as clean:
            encrypted = clipboard_crypto.encrypt_content(clean)
            with self._lock:
                self._conn.execute(
                    "INSERT INTO clipboard_history (content, timestamp) VALUES (?, ?)",
                    (encrypted, timestamp)
                )
                self._conn.commit()
            SecureMemory.clear_string(encrypted)

    def get_history(self, limit: int = 10):
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, content, timestamp FROM clipboard_history "
                "ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()

        history = []
        for r in rows:
            try:
                decrypted = clipboard_crypto.decrypt_content(r[1])
                history.append({
                    "id": r[0],
                    "content": decrypted,
                    "timestamp": r[2]
                })
            except Exception:
                continue

        return history

    def clear_history(self):
        with self._lock:
            self._conn.execute("DELETE FROM clipboard_history")
            self._conn.commit()

    def delete_entry(self, entry_id: int) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM clipboard_history WHERE id = ?",
                (entry_id,)
            )
            self._conn.commit()
            return cur.rowcount > 0
