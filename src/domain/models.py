from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class BriefSource:
    name: str
    url: str
    published_at: str

    @classmethod
    def from_dict(cls, payload: Dict[str, str]) -> "BriefSource":
        return cls(
            name=payload.get("name", "unknown"),
            url=payload.get("url", ""),
            published_at=payload.get("published_at", ""),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "url": self.url,
            "published_at": self.published_at,
        }


@dataclass(frozen=True)
class BriefItem:
    type: str
    title: str
    facts: List[str]
    sources: List[BriefSource]
    slug: str | None = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "BriefItem":
        return cls(
            type=payload.get("type", "politics"),
            title=payload.get("title", ""),
            facts=list(payload.get("facts", [])),
            sources=[
                BriefSource.from_dict(source) for source in payload.get("sources", [])
            ],
            slug=payload.get("slug"),
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "type": self.type,
            "title": self.title,
            "facts": self.facts,
            "sources": [source.to_dict() for source in self.sources],
        }
        if self.slug:
            payload["slug"] = self.slug
        return payload


@dataclass(frozen=True)
class CollectorPayload:
    date: str
    items: List[BriefItem]

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CollectorPayload":
        return cls(
            date=payload.get("date", ""),
            items=[BriefItem.from_dict(item) for item in payload.get("items", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(frozen=True)
class QualityResult:
    passed: bool
    reasons: List[str]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass": self.passed,
            "reasons": self.reasons,
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class PostDraft:
    category: str
    filename: str
    markdown_body: str
    summary: str
    sources: List[Dict[str, Any]]
