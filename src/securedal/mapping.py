# src/securedal/mapping.py
import sqlite3
import os
from abc import ABC, abstractmethod
from pathlib import Path


class AnchorMapping(ABC):
    """Abstract base class for anchor mappings. 
    Implement this to use a different mapping storage backend."""

    @abstractmethod
    def get(self, key: str) -> str | None:
        """Get CID for a given key. Returns None if not found."""
        ...

    @abstractmethod
    def set(self, key: str, cid: str) -> None:
        """Store key -> CID mapping."""
        ...

    @abstractmethod
    def delete(self, key: str) -> str | None:
        """Delete mapping for key. Returns the CID if it existed, None otherwise."""
        ...

    def close(self) -> None:
        """Optional cleanup on close."""
        pass


class SQLiteAnchorMapping(AnchorMapping):
    """Default SQLite-based anchor mapping."""

    def __init__(self, mapping_path: str = "./storage/mapping/tamper_mapping.db") -> None:
        db_file = Path(mapping_path)
        if db_file.suffix != ".db":
            db_file = db_file.with_suffix(".db")
        os.makedirs(db_file.parent, exist_ok=True)

        self._db = sqlite3.connect(str(db_file), check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS mapping (
                key  TEXT PRIMARY KEY,
                cid  TEXT NOT NULL
            )
        """)
        self._db.commit()

    def get(self, key: str) -> str | None:
        row = self._db.execute(
            "SELECT cid FROM mapping WHERE key = ?", (key,)
        ).fetchone()
        return row[0] if row else None

    def set(self, key: str, cid: str) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO mapping (key, cid) VALUES (?, ?)",
            (key, cid)
        )
        self._db.commit()

    def delete(self, key: str) -> str | None:
        row = self._db.execute(
            "SELECT cid FROM mapping WHERE key = ?", (key,)
        ).fetchone()
        if row:
            self._db.execute("DELETE FROM mapping WHERE key = ?", (key,))
            self._db.commit()
            return row[0]
        return None

    def close(self) -> None:
        self._db.close()