"""Obsidian vault indexer — scans .md files, creates FTS5."""

import re
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


def extract_frontmatter_tags(text):
    """Extract tags from YAML frontmatter."""
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    fm = parts[1]
    match = re.search(r"tags:\s*\[(.*?)\]", fm)
    if match:
        return [t.strip().strip('"') for t in match.group(1).split(",")]
    # YAML list format: tags:\n  - tag1\n  - tag2
    match = re.search(r"tags:\s*\n((?:\s*-\s*.+\n?)+)", fm)
    if match:
        return re.findall(r"-\s*(.+)", match.group(1))
    return []


def index_obsidian_vault(vault_path, db_path=None, exclude_tags=None):
    """Index all .md files in Obsidian vault into SQLite FTS5.

    Args:
        vault_path: path to Obsidian vault directory
        db_path: SQLite db path (default: vault_path/.obsidian-index.db)
        exclude_tags: tags to skip (default: ["draft", "daily"])
    Returns:
        dict with file_count, total_chars, errors
    """
    vault_path = Path(vault_path).expanduser()
    if not vault_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {vault_path}")

    db_path = Path(db_path or vault_path / ".obsidian-index.db")
    exclude_tags = exclude_tags or ["draft", "daily"]

    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS obsidian_fts
        USING fts5(path, title, content, tags)
    """)

    file_count = 0
    total_chars = 0
    errors = []

    for md_file in vault_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            tags = extract_frontmatter_tags(content)

            if any(t in tags for t in exclude_tags):
                continue

            title = md_file.stem
            rel_path = str(md_file.relative_to(vault_path))

            conn.execute(
                "INSERT INTO obsidian_fts (path, title, content, tags) VALUES (?, ?, ?, ?)",
                (rel_path, title, content, ",".join(tags)),
            )
            file_count += 1
            total_chars += len(content)
        except Exception as e:
            errors.append({"file": str(md_file), "error": str(e)})

    conn.commit()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS obsidian_meta (key TEXT PRIMARY KEY, value TEXT)"
    )
    conn.execute(
        "INSERT OR REPLACE INTO obsidian_meta VALUES (?, ?)",
        ("last_indexed", datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()

    return {"file_count": file_count, "total_chars": total_chars, "errors": errors}
