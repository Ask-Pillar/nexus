"""Module protocol — any module can implement these 3 methods to register with Nexus."""


class ModuleProtocol:
    name: str = ""
    weight: float = 0.1
    enabled: bool = False

    def search(self, query: str, top_k: int) -> list:
        raise NotImplementedError

    def import_source(self, source: str) -> int:
        raise NotImplementedError

    def stats(self) -> dict:
        raise NotImplementedError
