"""In-memory product search index (Redis-backed in production)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SearchResult:
    product_id: UUID
    sku: str
    name: str
    score: float


class ProductSearchIndex:
    def __init__(self) -> None:
        self._entries: list[dict] = []

    def index_product(self, *, product_id: UUID, sku: str, name: str, category: str | None) -> None:
        self._entries.append({
            "product_id": product_id,
            "sku": sku.upper(),
            "name": name.lower(),
            "category": (category or "").lower(),
        })

    def search(self, query: str, *, limit: int = 20) -> list[SearchResult]:
        if not query.strip():
            return []
        tokens = query.lower().split()
        results: list[SearchResult] = []
        for entry in self._entries:
            score = self._score(entry, tokens)
            if score > 0:
                results.append(SearchResult(
                    product_id=entry["product_id"],
                    sku=entry["sku"],
                    name=entry["name"],
                    score=score,
                ))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def _score(self, entry: dict, tokens: list[str]) -> float:
        score = 0.0
        for token in tokens:
            if token in entry["sku"].lower():
                score += 3.0
            if token in entry["name"]:
                score += 2.0
            if token in entry["category"]:
                score += 1.0
        return score

    def clear(self) -> None:
        self._entries.clear()
