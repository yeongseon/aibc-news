from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from zoneinfo import ZoneInfo

from ..config import DEFAULT_AUTHOR, CATEGORY_LABELS, KST_TZ
from ..utils import ensure_dir


class Publisher:
    def __init__(self, posts_dir: Path | None = None):
        self.posts_dir = posts_dir or Path("_posts")
        ensure_dir(self.posts_dir)

    def publish(
        self,
        run_date: str,
        markdown_body: str,
        summary: str,
        sources: List[Dict[str, Any]],
        category: str = "politics",
        filename: str = "",
        title: str = "",
        image: str | None = None,
        input_at: str | None = None,
        updated_at: str | None = None,
        author: str | None = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> Dict[str, Any]:
        if category not in CATEGORY_LABELS:
            raise ValueError(f"Unsupported category: {category}")

        if not filename:
            filename = f"{run_date}-politics-unknown.md"
        post_path = self.posts_dir / filename

        if post_path.exists() and not force:
            return {"status": "skipped", "path": str(post_path)}

        front_matter = self._build_front_matter(
            run_date,
            summary,
            sources,
            category,
            title=title,
            image=image,
            input_at=input_at,
            updated_at=updated_at,
        )
        author_line = f"\n\n작성자 {author}" if author else ""
        content = front_matter + "\n" + markdown_body + author_line + "\n"

        if dry_run:
            return {"status": "dry_run", "path": str(post_path), "content": content}

        post_path.write_text(content, encoding="utf-8")
        return {"status": "published", "path": str(post_path)}

    def _build_front_matter(
        self,
        run_date: str,
        summary: str,
        sources: List[Dict[str, Any]],
        category: str,
        title: str,
        image: str | None = None,
        input_at: str | None = None,
        updated_at: str | None = None,
    ) -> str:
        source_lines = "\n".join(
            f'  - "{source["name"]} - {source["url"]}"' for source in sources
        )
        category_label = CATEGORY_LABELS[category]
        image_line = f"image: {image}\n" if image else ""
        safe_title = title or category_label
        now_kst = datetime.now(ZoneInfo(KST_TZ)).strftime("%Y.%m.%d %H:%M KST")
        input_value = input_at or now_kst
        updated_value = updated_at or now_kst
        return (
            "---\n"
            "layout: single\n"
            f'title: "{safe_title}"\n'
            f"categories: [ {category} ]\n"
            f"date: {input_value}\n"
            f"created_at: {input_value}\n"
            f"updated_at: {updated_value}\n"
            f"input_at: {input_value}\n"
            f"{image_line}"
            f'summary: "{summary}"\n'
            "sources:\n"
            f"{source_lines}\n"
            "---\n"
        )
