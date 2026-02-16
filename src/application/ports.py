from __future__ import annotations

from typing import Dict, Any, List, Protocol, Tuple

from ..domain.models import QualityResult


class CollectorPort(Protocol):
    def collect(self, run_date: str) -> Dict[str, Any]: ...


class WriterPort(Protocol):
    def write_item(self, item: Dict[str, Any], run_date: str) -> Tuple[str, str]: ...


class QualityPort(Protocol):
    def validate(
        self, markdown: str, collector_payload: Dict[str, Any]
    ) -> Dict[str, object] | QualityResult: ...


class PublisherPort(Protocol):
    def publish(
        self,
        run_date: str,
        markdown_body: str,
        summary: str,
        sources: List[Dict[str, object]],
        category: str,
        filename: str,
        title: str = "",
        image: str | None = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> Dict[str, object]: ...


class LoggerPort(Protocol):
    def log(self, message: str) -> None: ...
