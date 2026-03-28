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


def test_make_filename_decodes_url_encoded_symbols() -> None:
    """Regression test: %5E in URL path must be decoded before slugifying."""
    item = {
        "type": "economy",
        "title": "S&P 500",
        "sources": [{"name": "Yahoo", "url": "https://finance.yahoo.com/quote/%5EGSPC"}],
    }
    filename = make_filename("2026-03-02", item, "2026.03.02 08:04 KST")
    assert filename == "2026-03-02-0804-economy-gspc.md"


def test_make_filename_decodes_kospi_symbol() -> None:
    item = {
        "type": "economy",
        "title": "코스피",
        "sources": [{"name": "Yahoo", "url": "https://finance.yahoo.com/quote/%5EKS11"}],
    }
    filename = make_filename("2026-02-23", item, "2026.02.23 15:30 KST")
    assert filename == "2026-02-23-1530-economy-ks11.md"
