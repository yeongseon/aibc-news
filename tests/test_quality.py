from src.collector import LocalCollector
from src.quality import QualityGate
from src.writer import SimpleWriter


def test_quality_passes_simple_writer():
    payload = LocalCollector().collect("2026-01-25")
    item = payload["items"][0]
    body, _ = SimpleWriter().write_item(item, payload["date"])
    result = QualityGate().validate(body, {"date": payload["date"], "items": [item]})
    assert result["pass"] is True


def test_quality_fails_forbidden_words():
    payload = LocalCollector().collect("2026-01-25")
    item = payload["items"][0]
    body, _ = SimpleWriter().write_item(item, payload["date"])
    body += "\n충격적인 소식"
    result = QualityGate().validate(body, {"date": payload["date"], "items": [item]})
    assert result["pass"] is False
