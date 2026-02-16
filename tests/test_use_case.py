import json
from pathlib import Path

import pytest

from src.application.use_case import RunDailyBriefUseCase


class _FakeCollector:
    def __init__(self, payload):
        self.payload = payload

    def collect(self, run_date: str):
        assert run_date == self.payload["date"]
        return self.payload


class _FakeWriter:
    def write_item(self, item, run_date: str):
        body = (
            "## 오늘의 주요 이슈\n\n"
            f"1) {item['title']} 소식입니다. 핵심 변화 흐름이 확인됐습니다. "
            f"발표일 {run_date} 기준으로 정리했습니다.\n"
        )
        return body, "요약"


class _FakeGate:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def validate(self, markdown, collector_payload):
        self.calls += 1
        return self.result


class _FakeGateSequence:
    def __init__(self, results):
        self.results = list(results)
        self.calls = 0

    def validate(self, markdown, collector_payload):
        self.calls += 1
        if self.calls <= len(self.results):
            return self.results[self.calls - 1]
        return self.results[-1]


class _FakePublisher:
    def publish(
        self,
        run_date: str,
        markdown_body: str,
        summary: str,
        sources: list[dict[str, object]],
        category: str,
        filename: str,
        title: str = "",
        image: str | None = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> dict[str, object]:
        assert category
        assert filename
        assert title
        return {
            "status": "published",
            "path": f"/tmp/{filename}",
            "dry_run": dry_run,
        }


class _FakeLogger:
    def __init__(self):
        self.messages = []

    def log(self, message: str) -> None:
        self.messages.append(message)


def test_use_case_writes_quality_artifact(tmp_path: Path) -> None:
    run_date = "2026-01-25"
    payload = {
        "date": run_date,
        "items": [
            {
                "type": "headline",
                "title": "정부 정책 동향",
                "facts": ["정책 발표", "지원 규모 확대"],
                "sources": [
                    {
                        "name": "과학기술정보통신부",
                        "url": "https://example.com/example",
                        "published_at": run_date,
                    }
                ],
            }
        ],
    }

    collector_path = tmp_path / "collector" / f"{run_date}.json"
    quality_path = tmp_path / "quality" / f"{run_date}.json"

    quality_result = {
        "pass": True,
        "reasons": [],
        "metrics": {
            "char_count": 180,
            "item_count": 1,
            "sources_total": 1,
            "sources_unique": 1,
        },
    }

    use_case = RunDailyBriefUseCase(
        collector=_FakeCollector(payload),
        writer=_FakeWriter(),
        gate=_FakeGate(quality_result),
        publisher=_FakePublisher(),
        logger=_FakeLogger(),
    )

    use_case.execute(
        run_date,
        collector_path=collector_path,
        quality_path=quality_path,
        dry_run=True,
        read_json=lambda path: json.loads(Path(path).read_text(encoding="utf-8")),
        write_json=lambda path, data: (
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            or Path(path).write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        ),
    )

    assert quality_path.exists()
    stored = json.loads(quality_path.read_text(encoding="utf-8"))

    assert stored["run_date"] == run_date
    assert len(stored["items"]) == 1
    assert stored["items"][0]["type"] == "headline"
    assert stored["items"][0]["title"] == "정부 정책 동향"
    assert stored["items"][0]["quality"] == quality_result


def test_use_case_writes_quality_artifact_on_failure(tmp_path: Path) -> None:
    run_date = "2026-01-25"
    payload = {
        "date": run_date,
        "items": [
            {
                "type": "market",
                "title": "코스피 급락",
                "facts": ["거래량 급감", "변동성 확대"],
                "sources": [
                    {
                        "name": "한국거래소",
                        "url": "https://example.com/krx",
                        "published_at": run_date,
                    }
                ],
            }
        ],
    }

    collector_path = tmp_path / "collector" / f"{run_date}.json"
    quality_path = tmp_path / "quality" / f"{run_date}.json"

    failure_result = {
        "pass": False,
        "reasons": ["테스트 실패 사유"],
        "metrics": {
            "char_count": 100,
            "item_count": 1,
            "sources_total": 1,
            "sources_unique": 1,
        },
    }

    use_case = RunDailyBriefUseCase(
        collector=_FakeCollector(payload),
        writer=_FakeWriter(),
        gate=_FakeGate(failure_result),
        publisher=_FakePublisher(),
        logger=_FakeLogger(),
    )

    with pytest.raises(SystemExit):
        use_case.execute(
            run_date,
            collector_path=collector_path,
            quality_path=quality_path,
            dry_run=True,
            read_json=lambda path: json.loads(Path(path).read_text(encoding="utf-8")),
            write_json=lambda path, data: (
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                or Path(path).write_text(
                    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            ),
        )

    assert quality_path.exists()
    stored = json.loads(quality_path.read_text(encoding="utf-8"))

    assert stored["run_date"] == run_date
    assert len(stored["items"]) == 1
    assert stored["items"][0]["type"] == "market"
    assert stored["items"][0]["quality"]["pass"] is False
    assert stored["items"][0]["quality"]["reasons"] == ["테스트 실패 사유"]


def test_use_case_artifact_includes_prior_successes_before_failure(
    tmp_path: Path,
) -> None:
    run_date = "2026-01-25"
    payload = {
        "date": run_date,
        "items": [
            {
                "type": "headline",
                "title": "정부 정책 발표",
                "facts": ["예산 확장", "세부안 발표"],
                "sources": [
                    {
                        "name": "과학기술정보통신부",
                        "url": "https://example.com/policy",
                        "published_at": run_date,
                    }
                ],
            },
            {
                "type": "market",
                "title": "AI 주가 급변",
                "facts": ["변동 확대", "거래량 집중"],
                "sources": [
                    {
                        "name": "한국거래소",
                        "url": "https://example.com/krx",
                        "published_at": run_date,
                    }
                ],
            },
        ],
    }

    collector_path = tmp_path / "collector" / f"{run_date}.json"
    quality_path = tmp_path / "quality" / f"{run_date}.json"

    quality_results = [
        {
            "pass": True,
            "reasons": [],
            "metrics": {
                "char_count": 250,
                "item_count": 1,
                "sources_total": 1,
                "sources_unique": 1,
            },
        },
        {
            "pass": False,
            "reasons": ["두 번째 항목 품질 미달"],
            "metrics": {
                "char_count": 80,
                "item_count": 1,
                "sources_total": 1,
                "sources_unique": 1,
            },
        },
    ]

    use_case = RunDailyBriefUseCase(
        collector=_FakeCollector(payload),
        writer=_FakeWriter(),
        gate=_FakeGateSequence(quality_results),
        publisher=_FakePublisher(),
        logger=_FakeLogger(),
    )

    with pytest.raises(SystemExit):
        use_case.execute(
            run_date,
            collector_path=collector_path,
            quality_path=quality_path,
            dry_run=True,
            read_json=lambda path: json.loads(Path(path).read_text(encoding="utf-8")),
            write_json=lambda path, data: (
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                or Path(path).write_text(
                    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            ),
        )

    assert quality_path.exists()
    stored = json.loads(quality_path.read_text(encoding="utf-8"))

    assert stored["run_date"] == run_date
    assert len(stored["items"]) == 2
    assert stored["items"][0]["type"] == "headline"
    assert stored["items"][0]["quality"]["pass"] is True
    assert stored["items"][1]["type"] == "market"
    assert stored["items"][1]["quality"]["pass"] is False
    assert stored["items"][1]["quality"]["reasons"] == ["두 번째 항목 품질 미달"]
