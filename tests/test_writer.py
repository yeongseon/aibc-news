from src.collector import LocalCollector
from src.writer import SimpleWriter


def test_writer_outputs_markdown():
    payload = LocalCollector().collect("2026-01-25")
    item = payload["items"][0]
    body, summary = SimpleWriter().write_item(item, payload["date"])

    assert body.startswith("1)")
    assert "1)" in body
    assert item["title"] in body
    assert summary
