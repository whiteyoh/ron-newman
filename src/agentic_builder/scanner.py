from __future__ import annotations

from collections import Counter
from pathlib import Path

from .models import FileInsight, FolderInsight


class FolderScanner:
    def scan(self, root: Path) -> FolderInsight:
        root = root.expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid folder path: {root}")

        extensions: Counter[str] = Counter()
        files: list[FileInsight] = []

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower() or "<no_ext>"
            extensions[ext] += 1
            files.append(
                FileInsight(
                    path=str(file_path.relative_to(root)),
                    extension=ext,
                    size_bytes=file_path.stat().st_size,
                )
            )

        files.sort(key=lambda f: f.path)
        return FolderInsight(
            root=root,
            file_count=len(files),
            extensions=dict(sorted(extensions.items())),
            files=files,
        )
