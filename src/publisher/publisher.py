from pathlib import Path
from typing import Dict, Any, List
import os

from ..config import DEFAULT_AUTHOR, CATEGORY_LABELS, DEFAULT_MODEL_NAME
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
        dry_run: bool = False,
        force: bool = False,
    ) -> Dict[str, Any]:
        if not filename:
            filename = f"{run_date}-politics-unknown.md"
        post_path = self.posts_dir / filename

        if post_path.exists() and not force:
            return {"status": "skipped", "path": str(post_path)}

        front_matter = self._build_front_matter(
            run_date, summary, sources, category, title=title, image=image
        )
        content = front_matter + "\n" + markdown_body + "\n"

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
    ) -> str:
        source_lines = "\n".join(
            f'  - "{source["name"]} - {source["url"]}"' for source in sources
        )
        category_label = CATEGORY_LABELS.get(category, category)
        model_name = os.environ.get("ARTICLE_MODEL_NAME", DEFAULT_MODEL_NAME)
        image_line = f"image: {image}\n" if image else ""
        safe_title = title or category_label
        return (
            "---\n"
            "layout: single\n"
            f'title: "{safe_title} - {model_name}"\n'
            f"author: {DEFAULT_AUTHOR}\n"
            f"categories: [ {category_label} ]\n"
            f"date: {run_date}\n"
            f"created_at: {run_date}\n"
            f"updated_at: {run_date}\n"
            f"{image_line}"
            f'summary: "{summary}"\n'
            "sources:\n"
            f"{source_lines}\n"
            "---\n"
        )
