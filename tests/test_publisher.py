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
