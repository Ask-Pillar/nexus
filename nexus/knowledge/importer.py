"""Knowledge importer — batch import with resume support.
Supports: .md .txt .jsonl .csv .pdf .png .jpg .jpeg"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

SUPPORTED_FORMATS = {".md", ".txt", ".jsonl", ".csv", ".pdf", ".png", ".jpg", ".jpeg"}


def _extract_text(filepath, llm_client=None):
    """Extract text from any supported format. Returns (text, method).
    llm_client: optional LLMClient for image/scan fallback.
    """
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
        # 1. pymupdf text layer
        try:
            import fitz
            doc = fitz.open(str(fp))
            pages = [page.get_text() for page in doc]
            doc.close()
            text = "\n".join(pages).strip()
            if len(text) > 100:
                return text, "pymupdf"
        except Exception:
            pass

        # 2. tesseract OCR per page (scanned PDF)
        try:
            import subprocess, tempfile
            doc = fitz.open(str(fp))
            ocr_pages = []
            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=200)
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    pix.save(tmp.name)
                    result = subprocess.run(
                        ["tesseract", tmp.name, "stdout"], capture_output=True, text=True, timeout=30
                    )
                    if result.stdout.strip():
                        ocr_pages.append(result.stdout.strip())
            doc.close()
            text = "\n".join(ocr_pages).strip()
            if len(text) > 50:
                return text, "pymupdf+ocr"
        except Exception:
            pass

        # 3. LLM vision fallback
        if llm_client:
            return _llm_describe_file(fp, "PDF文档", llm_client), "llm-vision"
        return f"[PDF: {fp.name}]", "path-only"

    if suffix in {".png", ".jpg", ".jpeg"}:
        text = _ocr_image(fp)
        if len(text) > 20:
            return text, "tesseract"
        if llm_client:
            return _llm_describe_file(fp, "图片", llm_client), "llm-vision"
        return f"[图片: {fp.name}]", "path-only"

    return "", "unknown"


def _ocr_image(fp):
    try:
        import subprocess
        result = subprocess.run(
            ["tesseract", str(fp), "stdout"], capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _llm_describe_file(fp, file_type, llm_client):
    """Use LLM vision to describe a file's content."""
    import base64
    content = fp.read_bytes()
    b64 = base64.b64encode(content).decode()

    prompt = {
        "role": "user",
        "content": [
            {"type": "text", "text": f"请详细描述这个{file_type}的内容，提取所有可见文字、表格数据、图表含义。如果是代码截图，请逐行转录代码。如果是流程图，请描述流程结构。"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
        ],
    }
    try:
        resp = llm_client.chat([prompt])
        return resp
    except Exception:
        return f"[{file_type}: {fp.name}，LLM 不可用]"


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
