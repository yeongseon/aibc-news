from src.collector import LocalCollector
from src.quality import QualityGate
from src.writer import SimpleWriter


def test_quality_passes_simple_writer():
    payload = LocalCollector().collect("2026-01-25")
    body, _ = SimpleWriter().write(payload)
    result = QualityGate().validate(body, payload)
    assert result["pass"] is True


def test_quality_fails_forbidden_words():
    payload = LocalCollector().collect("2026-01-25")
    body, _ = SimpleWriter().write(payload)
    body += "\n충격적인 소식"
    result = QualityGate().validate(body, payload)
    assert result["pass"] is False


def test_quality_fails_missing_sources():
    payload = LocalCollector().collect("2026-01-25")
    payload["items"][0]["sources"] = []
    body, _ = SimpleWriter().write(payload)
    result = QualityGate().validate(body, payload)
    assert result["pass"] is False


def test_quality_fails_source_ratio():
    payload = LocalCollector().collect("2026-01-25")
    for item in payload["items"]:
        item["sources"][0]["name"] = "동일출처"
    body, _ = SimpleWriter().write(payload)
    result = QualityGate().validate(body, payload)
    assert result["pass"] is False


def test_quality_fails_item_count_mismatch():
    payload = LocalCollector().collect("2026-01-25")
    body, _ = SimpleWriter().write(payload)
    payload["items"] = payload["items"][:3]
    result = QualityGate().validate(body, payload)
    assert result["pass"] is False
