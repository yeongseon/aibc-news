from src.collector import LocalCollector


def test_collector_schema():
    payload = LocalCollector().collect("2026-01-25")

    assert payload["date"] == "2026-01-25"
    assert 3 <= len(payload["items"]) <= 5

    for item in payload["items"]:
        assert item["type"]
        assert item["title"]
        assert isinstance(item["facts"], list)
        assert isinstance(item["sources"], list)
        assert item["sources"][0]["name"]
        assert item["sources"][0]["url"]
        assert item["sources"][0]["published_at"]
