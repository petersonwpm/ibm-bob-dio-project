"""Service layer — business logic for trilha operations."""

from dataclasses import dataclass

from model import Trilha, TrilhaRepository


@dataclass
class SearchResult:
    trilhas: list[Trilha]
    message: str
    found: bool


class TrilhaService:
    def __init__(self, repo: TrilhaRepository) -> None:
        self._repo = repo

    def all(self) -> list[Trilha]:
        return self._repo.all()

    def search(self, query: str) -> SearchResult:
        q = query.lower().strip()
        if not q:
            return SearchResult(
                trilhas=self._repo.all(),
                message="",
                found=True,
            )
        results = [
            t for t in self._repo.all() if q in t["name"].lower() or q in t["technology"].lower()
        ]
        if results:
            return SearchResult(
                trilhas=results,
                message=f"✔ {len(results)} trilha(s) encontrada(s).",
                found=True,
            )
        return SearchResult(
            trilhas=self._repo.all(),
            message="✘ Nenhuma trilha encontrada. Mostrando todas.",
            found=False,
        )
