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


def test_publisher_idempotent(tmp_path: Path):
    publisher = Publisher(posts_dir=tmp_path)
    first = publisher.publish(
        run_date="2026-01-25",
        markdown_body="## 테스트\n\n1) 내용입니다.",
        summary="요약",
        sources=[{"name": "출처", "url": "https://example.com"}],
    )
    second = publisher.publish(
        run_date="2026-01-25",
        markdown_body="## 테스트\n\n1) 내용입니다.",
        summary="요약",
        sources=[{"name": "출처", "url": "https://example.com"}],
    )

    assert first["status"] == "published"
    assert second["status"] == "skipped"


def test_publisher_dry_run_format(tmp_path: Path):
    publisher = Publisher(posts_dir=tmp_path)
    result = publisher.publish(
        run_date="2026-01-25",
        markdown_body="## 테스트\n\n1) 내용입니다.",
        summary="오늘의 핵심 요약",
        sources=[
            {"name": "출처1", "url": "https://example.com/1"},
            {"name": "출처2", "url": "https://example.com/2"},
        ],
        dry_run=True,
    )

    content = result["content"]
    assert content.startswith("---\n")
    assert "layout: post" in content
    assert "title: \"[AIBC 브리핑] 2026-01-25 주요 이슈\"" in content
    assert "author: AIBC Desk" in content
    assert "categories: [ News ]" in content
    assert "date: 2026-01-25" in content
    assert "summary: \"오늘의 핵심 요약\"" in content
    assert "sources:" in content
    assert "  - \"출처1 - https://example.com/1\"" in content
    assert "  - \"출처2 - https://example.com/2\"" in content
    assert "---\n## 테스트" in content
