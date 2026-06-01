"""Nexus Core — 调度层：路由 + 合并 + 配置"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))

from sisyphus.memory.unified import UnifiedRetriever
from sisyphus.memory.pools import PoolRegistry
from sisyphus.memory.store import MemoryStore
from sisyphus.memory.context import AgentMemory


class NexusCore:
    def __init__(self):
        self.registry = PoolRegistry()
        self.registry.init_structure()
        self.retriever = UnifiedRetriever()
        self.config = self.registry.config

    def search(self, query, scope=None, top_k=10):
        return self.retriever.retrieve(query, scope, top_k)

    def get_context(self, query, max_chars=3000):
        store = self.registry.get_store("personal")
        mem = AgentMemory(store)
        return mem.before_turn(query, max_chars)

    def write(self, title, content, mem_type="lesson", tags=None):
        store = self.registry.get_store("personal")
        return store.create_if_new(title=title, type=mem_type, content=content, tags=tags or [])

    def stats(self):
        return {
            "personal": len(self.registry.get_store("personal").list()),
            "project": len(self.registry.get_store("projects", self.registry.current_project_hash()).list()),
            "pools": self.registry.active_pools(),
        }
