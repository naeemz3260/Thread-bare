"""
Helpers for walking a project directory and picking out source files worth scanning.
"""

import os

EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".php": "php",
    ".java": "java",
    ".rb": "ruby",
    ".go": "go",
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".html": "html",
    ".sql": "sql",
}

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__",
    "dist", "build", ".next", "vendor", "reports",
}

MAX_FILE_SIZE_BYTES = 200_000  # skip huge generated/minified files


def discover_source_files(root_dir: str) -> list[str]:
    """Return a list of file paths under root_dir worth scanning."""
    matches = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in EXTENSION_LANGUAGE_MAP:
                full_path = os.path.join(dirpath, filename)
                try:
                    if os.path.getsize(full_path) <= MAX_FILE_SIZE_BYTES:
                        matches.append(full_path)
                except OSError:
                    continue
    return sorted(matches)


def read_file_safely(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def get_language(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    return EXTENSION_LANGUAGE_MAP.get(ext, "text")
