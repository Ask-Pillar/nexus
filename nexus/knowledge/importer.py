"""Knowledge importer — batch import with resume support.
Supports: .md .txt .jsonl .csv .pdf .png .jpg .jpeg"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

SUPPORTED_FORMATS = {".md", ".txt", ".jsonl", ".csv", ".pdf", ".png", ".jpg", ".jpeg"}


def _extract_text(filepath):
    """Extract text from any supported format. Returns (text, method)."""
    fp = Path(filepath)
    suffix = fp.suffix.lower()

    if suffix in {".md", ".txt"}:
        return fp.read_text(encoding="utf-8"), "raw"

    if suffix == ".jsonl":
        chunks = []
        for line in fp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                chunks.append(obj.get("content", obj.get("text", json.dumps(obj))))
            except json.JSONDecodeError:
                chunks.append(line.strip())
        return "\n".join(chunks), "jsonl"

    if suffix == ".csv":
        import csv
        rows = []
        with open(fp, newline="") as f:
            for row in csv.DictReader(f):
                rows.append(str(dict(row)))
        return "\n".join(rows), "csv"

    if suffix == ".pdf":
        try:
            import fitz  # pymupdf
            doc = fitz.open(str(fp))
            pages = [page.get_text() for page in doc]
            doc.close()
            return "\n".join(pages), "pymupdf"
        except ImportError:
            raise RuntimeError("pymupdf not installed: pip install pymupdf")

    if suffix in {".png", ".jpg", ".jpeg"}:
        # Try OCR first, fall back to description
        try:
            import subprocess
            result = subprocess.run(
                ["tesseract", str(fp), "stdout"], capture_output=True, text=True, timeout=30
            )
            text = result.stdout.strip()
            if text:
                return text, "tesseract"
        except Exception:
            pass
        # Fallback: store path as description for later llama-vision processing
        return f"[图片: {fp.name}]", "path-only"

    return "", "unknown"


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
                method TEXT,
                imported_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def import_file(self, filepath):
        filepath = Path(filepath)
        text, method = _extract_text(filepath)
        if not text.strip():
            return {"status": "skipped", "reason": "no text extracted"}

        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO knowledge_fts (source, content) VALUES (?, ?)",
            (str(filepath), text[:50_000]),
        )
        conn.execute(
            "INSERT OR REPLACE INTO import_log VALUES (?, ?, ?, ?)",
            (str(filepath), len(text.encode()), method, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()
        return {"status": "ok", "method": method, "source": str(filepath)}

    def import_directory(self, dir_path, formats=None, progress=None):
        dir_path = Path(dir_path)
        formats = formats or SUPPORTED_FORMATS
        all_files = sorted(
            f for f in dir_path.rglob("*")
            if f.suffix.lower() in formats and f.is_file()
        )
        results = {"files_done": 0, "errors": []}

        for i, fp in enumerate(all_files, 1):
            if progress:
                progress(i, len(all_files))
            try:
                self.import_file(fp)
                results["files_done"] += 1
            except Exception as e:
                results["errors"].append({"file": str(fp), "error": str(e)})
        return results

    def search(self, query, top_k=10):
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT source, snippet(knowledge_fts, 1, '<mark>', '</mark>', '...', 40) "
            "FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, top_k),
        ).fetchall()
        conn.close()
        return [{"source": r[0], "snippet": r[1]} for r in rows]
