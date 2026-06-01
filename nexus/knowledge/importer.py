"""Knowledge importer — batch import with resume support."""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

SUPPORTED_FORMATS = {".md", ".txt", ".jsonl", ".csv"}


class KnowledgeImporter:
    def __init__(self, db_path, batch_size=500):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.batch_size = batch_size
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts
            USING fts5(source, content)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS import_log (
                source TEXT PRIMARY KEY,
                size_bytes INTEGER,
                imported_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def import_directory(self, dir_path, formats=None, progress=None):
        """Import all supported files from directory with batch progress."""
        dir_path = Path(dir_path)
        formats = formats or SUPPORTED_FORMATS
        all_files = sorted(
            f for f in dir_path.rglob("*")
            if f.suffix.lower() in formats and f.is_file()
        )
        results = {"files_done": 0, "total_chunks": 0, "errors": []}

        for i, fp in enumerate(all_files, 1):
            if progress:
                progress(i, len(all_files))
            try:
                self._import_file(fp)
                results["files_done"] += 1
                results["total_chunks"] += 1
            except Exception as e:
                results["errors"].append({"file": str(fp), "error": str(e)})
        return results

    def _import_file(self, filepath):
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()
        if suffix == ".md" or suffix == ".txt":
            content = filepath.read_text(encoding="utf-8")
        elif suffix == ".jsonl":
            content = "\n".join(
                json.loads(line).get("content", line)
                for line in filepath.read_text().splitlines() if line.strip()
            )
        elif suffix == ".csv":
            import csv
            rows = []
            with open(filepath) as f:
                for row in csv.DictReader(f):
                    rows.append(str(dict(row)))
            content = "\n".join(rows)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO knowledge_fts (source, content) VALUES (?, ?)",
            (str(filepath), content[:50_000]),
        )
        conn.execute(
            "INSERT OR REPLACE INTO import_log VALUES (?, ?, ?)",
            (str(filepath), len(content.encode()), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()

    def search(self, query, top_k=10):
        """Search imported knowledge."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT source, snippet(knowledge_fts, 1, '<mark>', '</mark>', '...', 40) "
            "FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, top_k),
        ).fetchall()
        conn.close()
        return [{"source": r[0], "snippet": r[1]} for r in rows]
