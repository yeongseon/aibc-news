from pathlib import Path

import pytest

from src.publisher import Publisher


def test_publisher_dry_run(tmp_path: Path):
    publisher = Publisher(posts_dir=tmp_path)
    result = publisher.publish(
        run_date="2026-01-25",
        markdown_body="## 테스트\n\n1) 내용입니다.",
        summary="요약",
        sources=[{"name": "출처", "url": "https://example.com"}],
        category="economy",
        dry_run=True,
    )

    assert result["status"] == "dry_run"
    assert not (tmp_path / "2026-01-25-aibc-briefing.md").exists()
    assert "categories: [ economy ]" in result["content"]


def test_publisher_rejects_unsupported_category(tmp_path: Path):
    publisher = Publisher(posts_dir=tmp_path)

    with pytest.raises(ValueError, match="Unsupported category"):
        publisher.publish(
            run_date="2026-01-25",
            markdown_body="본문",
            summary="요약",
            sources=[{"name": "출처", "url": "https://example.com"}],
            category="market",
            dry_run=True,
        )


def test_publisher_sanitizes_bad_filename(tmp_path: Path):
    publisher = Publisher(posts_dir=tmp_path)
    result = publisher.publish(
        run_date="2026-02-17",
        markdown_body="## Test",
        summary="summary",
        sources=[{"name": "src", "url": "https://example.com"}],
        category="economy",
        filename="2026-02-17-2251-economy-latest?from=USD&to=KRW.md",
        dry_run=True,
    )
    # ? and = should be sanitized out
    assert "?" not in result["path"]
    assert "=" not in result["path"]
    assert result["path"].endswith(".md")


def test_publisher_sanitizes_percent_encoded_filename(tmp_path: Path):
    publisher = Publisher(posts_dir=tmp_path)
    result = publisher.publish(
        run_date="2026-03-02",
        markdown_body="## Test",
        summary="summary",
        sources=[{"name": "src", "url": "https://example.com"}],
        category="economy",
        filename="2026-03-02-0804-economy-%5egspc.md",
        dry_run=True,
    )
    # %5e should be sanitized out (% is not alphanumeric)
    assert "%" not in result["path"]
    assert result["path"].endswith(".md")
