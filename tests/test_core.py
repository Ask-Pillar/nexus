"""Tests for Nexus core and knowledge layer."""

import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nexus.core import NexusCore
from nexus.knowledge.importer import KnowledgeImporter
from nexus.knowledge.obsidian import index_obsidian_vault


class TestNexusCore:
    def test_search_and_write(self):
        core = NexusCore()
        core.write(title="test", content="hello world", mem_type="lesson")
        results = core.search("test")
        assert len(results) >= 1

    def test_context(self):
        core = NexusCore()
        ctx = core.get_context("test")
        assert isinstance(ctx, str)


class TestKnowledgeImporter:
    def test_import_and_search(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Hello\n\nThis is a test.")
        importer = KnowledgeImporter(tmp_path / "kb.db")
        importer._import_file(f)
        results = importer.search("test")
        assert len(results) >= 1


class TestObsidianIndexer:
    def test_index_vault(self, tmp_path):
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "permanent.md").write_text("---\ntags: [permanent]\n---\n# Note\nContent here.")
        (vault / "draft.md").write_text("---\ntags: [draft]\n---\nDraft content.")
        result = index_obsidian_vault(str(vault), db_path=str(tmp_path / "obsidian.db"))
        assert result["file_count"] == 1  # draft excluded
