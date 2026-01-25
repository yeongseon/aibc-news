from pathlib import Path

from src.publisher import Publisher


def test_publisher_dry_run(tmp_path: Path):
    publisher = Publisher(posts_dir=tmp_path)
    result = publisher.publish(
        run_date="2026-01-25",
        markdown_body="## 테스트\n\n1) 내용입니다.",
        summary="요약",
        sources=[{"name": "출처", "url": "https://example.com"}],
        dry_run=True,
    )

    assert result["status"] == "dry_run"
    assert not (tmp_path / "2026-01-25-aibc-briefing.md").exists()
