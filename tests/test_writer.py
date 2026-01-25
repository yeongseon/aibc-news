from src.collector import LocalCollector
from src.writer import SimpleWriter


def test_writer_outputs_markdown():
    payload = LocalCollector().collect("2026-01-25")
    body, summary = SimpleWriter().write(payload)

    assert body.startswith("## 오늘의 주요 이슈")
    assert "1)" in body
    assert "2)" in body
    assert summary
