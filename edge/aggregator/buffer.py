import sqlite3
import json
import time
import structlog
from typing import Dict, Any, List, Tuple

from edge.config.settings import config

logger = structlog.get_logger(__name__)

class SQLiteBuffer:
    """Stores payloads locally when network transmission to CCC fails."""
    def __init__(self):
        self.db_path = config.paths.buffer_db
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # SEC-L3: WAL mode for power-cut resilience on Pi
                cursor.execute('PRAGMA journal_mode=WAL')
                cursor.execute('PRAGMA synchronous=NORMAL')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS buffer (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        payload TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        attempts INTEGER DEFAULT 0
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error("buffer_init_error", error=str(e))

    def push(self, payload: Dict[str, Any]) -> None:
        try:
            payload_str = json.dumps(payload)
            now = time.time()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO buffer (payload, created_at) VALUES (?, ?)",
                    (payload_str, now)
                )
                conn.commit()
                
                cursor.execute("SELECT COUNT(*) FROM buffer")
                count = cursor.fetchone()[0]
                
                logger.info("buffer_push", size=count)
        except sqlite3.Error as e:
            logger.error("buffer_push_error", error=str(e))

    def peek_batch(self, limit: int = 10) -> List[Tuple[int, Dict[str, Any]]]:
        """C4: Return (id, payload) pairs WITHOUT deleting. Caller confirms send
        then calls delete_ids() to remove. Prevents data loss on send failure."""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, payload FROM buffer ORDER BY created_at ASC LIMIT ?", 
                    (limit,)
                )
                rows = cursor.fetchall()
                
                for row in rows:
                    try:
                        results.append((row[0], json.loads(row[1])))
                    except json.JSONDecodeError:
                        logger.error("buffer_decode_error", id=row[0])
                
                logger.info("buffer_peek", count=len(results))
        except sqlite3.Error as e:
            logger.error("buffer_peek_error", error=str(e))
            
        return results

    def delete_ids(self, ids: List[int]) -> None:
        """Delete confirmed-sent records by id."""
        if not ids:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' for _ in ids)
                cursor.execute(f"DELETE FROM buffer WHERE id IN ({placeholders})", ids)
                conn.commit()
                logger.info("buffer_delete", count=len(ids))
        except sqlite3.Error as e:
            logger.error("buffer_delete_error", error=str(e))



    def size(self) -> int:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM buffer")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error("buffer_size_error", error=str(e))
            return 0
