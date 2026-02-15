from pathlib import Path
from typing import Dict, Any, List
import subprocess

from ..config import DEFAULT_AUTHOR
from ..utils import ensure_dir


class Publisher:
    def __init__(self, posts_dir: Path | None = None, repo_root: Path | None = None):
        self.posts_dir = posts_dir or Path("_posts")
        self.repo_root = repo_root or Path(".")
        ensure_dir(self.posts_dir)

    def publish(
        self,
        run_date: str,
        markdown_body: str,
        summary: str,
        sources: List[Dict[str, Any]],
        category: str = "news",
        filename: str = "",
        dry_run: bool = False,
        force: bool = False,
    ) -> Dict[str, Any]:
        if not filename:
            filename = f"{run_date}-news-unknown.md"
        post_path = self.posts_dir / filename

        if post_path.exists() and not force:
            return {"status": "skipped", "path": str(post_path)}

        front_matter = self._build_front_matter(run_date, summary, sources, category)
        content = front_matter + "\n" + markdown_body + "\n"

        if dry_run:
            return {"status": "dry_run", "path": str(post_path), "content": content}

        post_path.write_text(content, encoding="utf-8")
        return {"status": "published", "path": str(post_path)}

    def commit_changes(self, message: str) -> Dict[str, Any]:
        try:
            subprocess.check_call(
                ["git", "add", "_posts", "data", "logs"],
                cwd=self.repo_root,
            )
            subprocess.check_call(
                ["git", "diff", "--quiet", "--staged"],
                cwd=self.repo_root,
            )
            return {"status": "skipped"}
        except subprocess.CalledProcessError:
            pass

        subprocess.check_call(
            ["git", "config", "user.email", "action@github.com"],
            cwd=self.repo_root,
        )
        subprocess.check_call(
            ["git", "config", "user.name", "GitHub Action"],
            cwd=self.repo_root,
        )
        subprocess.check_call(
            ["git", "commit", "-m", message],
            cwd=self.repo_root,
        )
        subprocess.check_call(["git", "push"], cwd=self.repo_root)
        return {"status": "pushed"}

    def _build_front_matter(
        self, run_date: str, summary: str, sources: List[Dict[str, Any]], category: str
    ) -> str:
        source_lines = "\n".join(
            f'  - "{source["name"]} - {source["url"]}"' for source in sources
        )
        return (
            "---\n"
            "layout: single\n"
            f'title: "[AIBC 브리핑] {run_date} {category.upper()}"\n'
            f"author: {DEFAULT_AUTHOR}\n"
            f"categories: [ {category} ]\n"
            f"date: {run_date}\n"
            f'summary: "{summary}"\n'
            "sources:\n"
            f"{source_lines}\n"
            "---\n"
        )
