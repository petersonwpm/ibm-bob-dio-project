"""Model layer — data types and repository. No curses dependency."""

import json
from typing import TypedDict


class Promotion(TypedDict):
    discount: str
    valid_until: str
    description: str


class Live(TypedDict):
    title: str
    date: str


class Trilha(TypedDict):
    id: int
    name: str
    technology: str
    level: str
    modules: int
    total_xp: int
    available_badges: list[str]
    promotions: Promotion
    lifetime: bool
    lives: list[Live]


class TrilhaRepository:
    def __init__(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            self._data: list[Trilha] = json.load(f)["trilhas"]

    def all(self) -> list[Trilha]:
        return self._data

    def search(self, query: str) -> list[Trilha]:
        q = query.lower().strip()
        if not q:
            return self._data
        return [t for t in self._data if q in t["name"].lower() or q in t["technology"].lower()]
