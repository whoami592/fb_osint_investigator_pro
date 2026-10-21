"""Local SQLite storage for cases, URLs, notes, and evidence metadata."""
from __future__ import annotations
import os, sqlite3
from pathlib import Path
from .core import utc_now, validate_facebook_url, sha256_file

def data_dir() -> Path:
    p = Path(os.environ.get("FBOSINT_HOME", Path.cwd() / "data")).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p

class Store:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else data_dir() / "cases.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self):
        with self._connect() as c:
            c.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS cases (
              id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
              owner TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS urls (
              id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
              url TEXT NOT NULL, label TEXT NOT NULL, added_at TEXT NOT NULL,
              FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS notes (
              id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
              note TEXT NOT NULL, added_at TEXT NOT NULL,
              FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS evidence (
              id INTEGER PRIMARY KEY AUTOINCREMENT, case_id INTEGER NOT NULL,
              filename TEXT NOT NULL, description TEXT NOT NULL, sha256 TEXT NOT NULL,
              size_bytes INTEGER NOT NULL, added_at TEXT NOT NULL,
              FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
            );
            """)

    def create_case(self, title: str, owner: str) -> int:
        title, owner = title.strip(), owner.strip()
        if not title or not owner: raise ValueError("Case title and owner are required")
        with self._connect() as c:
            cur = c.execute("INSERT INTO cases(title,owner,created_at) VALUES(?,?,?)",
                            (title[:200], owner[:120], utc_now()))
            return int(cur.lastrowid)

    def list_cases(self):
        with self._connect() as c:
            return [dict(r) for r in c.execute("SELECT * FROM cases ORDER BY id DESC")]

    def add_url(self, case_id: int, url: str, label: str = "Public URL"):
        safe_url = validate_facebook_url(url)
        with self._connect() as c:
            self._require_case(c, case_id)
            c.execute("INSERT INTO urls(case_id,url,label,added_at) VALUES(?,?,?,?)",
                      (case_id, safe_url, label.strip()[:200] or "Public URL", utc_now()))

    def add_note(self, case_id: int, note: str):
        note = note.strip()
        if not note: raise ValueError("Note cannot be empty")
        with self._connect() as c:
            self._require_case(c, case_id)
            c.execute("INSERT INTO notes(case_id,note,added_at) VALUES(?,?,?)",
                      (case_id, note[:10000], utc_now()))

    def add_evidence(self, case_id: int, path: str, description: str):
        digest, size = sha256_file(path)
        with self._connect() as c:
            self._require_case(c, case_id)
            c.execute("""INSERT INTO evidence(case_id,filename,description,sha256,size_bytes,added_at)
                         VALUES(?,?,?,?,?,?)""",
                      (case_id, Path(path).name[:255], description.strip()[:1000],
                       digest, size, utc_now()))

    @staticmethod
    def _require_case(con, case_id):
        if con.execute("SELECT id FROM cases WHERE id=?", (case_id,)).fetchone() is None:
            raise ValueError(f"Case {case_id} does not exist")

    def get_case(self, case_id: int):
        with self._connect() as c:
            case = c.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
            if case is None: raise ValueError(f"Case {case_id} does not exist")
            result = dict(case)
            for table in ("urls", "notes", "evidence"):
                result[table] = [dict(r) for r in c.execute(
                    f"SELECT * FROM {table} WHERE case_id=? ORDER BY id", (case_id,))]
            return result
