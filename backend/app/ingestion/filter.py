# backend/app/ingestion/filter.py
import os
from typing import Set

IGNORED_DIRECTORIES: Set[str] = {
    ".git", ".github", "node_modules", "dist", "build", "coverage",
    "__pycache__", ".venv", "venv", "env", "target", "vendor",
    ".next", ".cache", ".idea", ".vscode", "bin", "obj", ".turbo",
    "out", "public", ".gradle", ".pipeline"
}

IGNORED_EXTENSIONS: Set[str] = {
    # Binaries & executables
    ".exe", ".dll", ".so", ".dylib", ".bin", ".iso", ".dmg", ".class", ".pyc", ".o", ".a",
    # Images & Media
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".mp4", ".mov", ".avi", ".mp3", ".wav",
    # Archives & Compressed
    ".zip", ".tar", ".gz", ".7z", ".rar", ".bz2", ".xz",
    # Fonts
    ".ttf", ".woff", ".woff2", ".eot", ".otf",
    # Data dumps & huge binaries
    ".sqlite", ".db", ".parquet", ".pkl", ".h5", ".onnx",
    # Lockfiles and minified code
    ".lock", ".map", ".min.js", ".min.css", ".bundle.js"
}

IGNORED_EXACT_FILES: Set[str] = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "Pipfile.lock", "Cargo.lock", "composer.lock", "go.sum"
}

SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".docx": "Word",
    ".doc": "Word",
    ".pdf": "PDF",
    ".ipynb": "Jupyter Notebook",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sql": "SQL",
    ".md": "Markdown",
    ".markdown": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
}


def is_file_supported(file_path: str, file_size_bytes: int, max_file_size_kb: int = 500) -> bool:
    """
    Evaluates whether a repository file should be indexed.
    """
    if file_size_bytes > (max_file_size_kb * 1024):
        return False

    parts = file_path.replace("\\", "/").split("/")
    for part in parts[:-1]:
        if part in IGNORED_DIRECTORIES or part.startswith("."):
            return False

    filename = parts[-1]
    if filename in IGNORED_EXACT_FILES or filename.startswith("."):
        return False

    _, ext = os.path.splitext(filename.lower())
    if ext in IGNORED_EXTENSIONS:
        return False

    return ext in SUPPORTED_EXTENSIONS


def detect_language(file_path: str) -> str:
    _, ext = os.path.splitext(file_path.lower())
    return SUPPORTED_EXTENSIONS.get(ext, "Unknown")