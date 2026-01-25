from src.collector import LocalCollector, collect_with_retry, validate_payload


def test_collector_schema():
    payload = LocalCollector().collect("2026-01-25")

    assert payload["date"] == "2026-01-25"
    assert 3 <= len(payload["items"]) <= 5

    validate_payload(payload)

    for item in payload["items"]:
        assert item["type"]
        assert item["title"]
        assert isinstance(item["facts"], list)
        assert isinstance(item["sources"], list)
        assert item["sources"][0]["name"]
        assert item["sources"][0]["url"]
        assert item["sources"][0]["published_at"]


def test_collector_retry_recovers():
    from src.collector.base import Collector

    class FlakyCollector(Collector):
        def __init__(self):
            self.calls = 0

        def collect(self, run_date: str):
            self.calls += 1
            if self.calls < 3:
                raise RuntimeError("temporary")
            return LocalCollector().collect(run_date)

    payload = collect_with_retry(
        FlakyCollector(),
        "2026-01-25",
        retries=2,
        sleep_seconds=0,
    )
    validate_payload(payload)
