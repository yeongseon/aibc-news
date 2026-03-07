from src.slug import make_filename, slugify


def test_slugify_normalizes_non_alnum_sequences() -> None:
    assert slugify("Latest?from=USD&to=KRW") == "latest-from-usd-to-krw"


def test_make_filename_sanitizes_economy_source_query_params() -> None:
    item = {
        "type": "economy",
        "title": "원달러 환율",
        "sources": [{"name": "FX", "url": "https://example.com/latest?from=USD&to=KRW"}],
    }

    filename = make_filename("2026-02-17", item, "2026.02.17 22:51 KST")

    assert filename == "2026-02-17-2251-economy-latest-from-usd-to-krw.md"
