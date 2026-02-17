import json
from pathlib import Path

import pytest

from src.publisher.ready_news import load_ready_items, publish_ready_items


def test_load_ready_items_filters_category(tmp_path: Path) -> None:
    run_date = "2026-02-16"
    ready_dir = tmp_path / "ready-news" / run_date
    ready_dir.mkdir(parents=True, exist_ok=True)

    economy_item = {
        "category": "economy",
        "title": "코스피 동향",
        "summary": "요약",
        "body": "본문",
        "meta": {
            "input_at": "2026.02.16 09:00 KST",
            "updated_at": "2026.02.16 09:10 KST",
        },
        "sources": [{"name": "Yahoo Finance", "url": "https://finance.yahoo.com/"}],
    }
    weather_item = {
        "category": "weather",
        "title": "날씨 동향",
        "summary": "요약",
        "body": "본문",
        "meta": {
            "input_at": "2026.02.16 09:00 KST",
            "updated_at": "2026.02.16 09:10 KST",
        },
        "sources": [{"name": "OpenWeather", "url": "https://openweathermap.org"}],
    }

    (ready_dir / "economy.json").write_text(
        json.dumps(economy_item, ensure_ascii=False), encoding="utf-8"
    )
    (ready_dir / "weather.json").write_text(
        json.dumps(weather_item, ensure_ascii=False), encoding="utf-8"
    )

    items = load_ready_items(
        ready_dir=tmp_path / "ready-news", run_date=run_date, category="economy"
    )

    assert len(items) == 1
    assert items[0]["category"] == "economy"
    assert items[0]["date"] == run_date


def test_load_ready_items_rejects_invalid_category(tmp_path: Path) -> None:
    run_date = "2026-02-16"
    ready_dir = tmp_path / "ready-news" / run_date
    ready_dir.mkdir(parents=True, exist_ok=True)

    invalid_item = {
        "category": "market",
        "title": "시장",
        "summary": "요약",
        "body": "본문",
        "meta": {
            "input_at": "2026.02.16 09:00 KST",
            "updated_at": "2026.02.16 09:10 KST",
        },
        "sources": [{"name": "출처", "url": "https://example.com"}],
    }
    (ready_dir / "market.json").write_text(
        json.dumps(invalid_item, ensure_ascii=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Unsupported category"):
        load_ready_items(ready_dir=tmp_path / "ready-news", run_date=run_date)


def test_publish_ready_items_dry_run(tmp_path: Path) -> None:
    items = [
        {
            "date": "2026-02-16",
            "category": "economy",
            "title": "코스피 동향",
            "summary": "요약",
            "body": "본문",
            "sources": [{"name": "Yahoo Finance", "url": "https://finance.yahoo.com/"}],
        }
    ]

    results = publish_ready_items(items, dry_run=True, force=False, posts_dir=tmp_path)

    assert len(results) == 1
    assert results[0]["status"] == "dry_run"
    assert "categories: [ economy ]" in results[0]["content"]


def test_publish_ready_items_uses_media_hero_image(tmp_path: Path) -> None:
    items = [
        {
            "date": "2026-02-16",
            "category": "economy",
            "title": "코스피 동향",
            "summary": "요약",
            "body": "본문",
            "sources": [{"name": "Yahoo Finance", "url": "https://finance.yahoo.com/"}],
            "media": {
                "hero_image": {
                    "url": "/assets/images/2026-02-16/ks11.webp",
                    "alt": "코스피 지수 차트",
                }
            },
        }
    ]

    results = publish_ready_items(items, dry_run=True, force=False, posts_dir=tmp_path)

    assert results[0]["status"] == "dry_run"
    assert "image: /assets/images/2026-02-16/ks11.webp" in results[0]["content"]


def test_load_ready_items_rejects_media_without_alt(tmp_path: Path) -> None:
    run_date = "2026-02-16"
    ready_dir = tmp_path / "ready-news" / run_date
    ready_dir.mkdir(parents=True, exist_ok=True)

    invalid_item = {
        "category": "economy",
        "title": "시장",
        "summary": "요약",
        "body": "본문",
        "meta": {
            "input_at": "2026.02.16 09:00 KST",
            "updated_at": "2026.02.16 09:10 KST",
        },
        "sources": [{"name": "출처", "url": "https://example.com"}],
        "media": {
            "hero_image": {
                "url": "/assets/images/market.webp",
            }
        },
    }
    (ready_dir / "market.json").write_text(
        json.dumps(invalid_item, ensure_ascii=False), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="media.hero_image.alt"):
        load_ready_items(ready_dir=tmp_path / "ready-news", run_date=run_date)
