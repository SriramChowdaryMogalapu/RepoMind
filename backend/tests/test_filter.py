# backend/tests/test_filter.py
from app.ingestion.filter import is_file_supported, detect_language


def test_supported_files():
    print("\n[TEST] Testing supported source files filtering...")
    valid_files = [
        ("src/main.py", 1024),
        ("components/App.tsx", 5000),
        ("server/index.js", 2048),
        ("docs/README.md", 300),
        ("queries/schema.sql", 1500),
    ]
    for path, size in valid_files:
        supported = is_file_supported(path, size)
        print(f"[TEST] Checking '{path}' ({size} bytes) -> Supported: {supported}")
        assert supported is True


def test_ignored_files_and_directories():
    print("\n[TEST] Testing ignored files and forbidden directories...")
    invalid_files = [
        ("node_modules/react/index.js", 1024),
        (".git/config", 500),
        (".venv/lib/python3.11/site.py", 2000),
        ("dist/bundle.js", 10000),
        ("src/assets/logo.png", 50000),
        ("package-lock.json", 100000),
        ("build/app.min.js", 5000),
        ("large_file.py", 600 * 1024),  # > 500 KB default limit
    ]
    for path, size in invalid_files:
        supported = is_file_supported(path, size, max_file_size_kb=500)
        print(f"[TEST] Checking '{path}' ({size} bytes) -> Supported: {supported}")
        assert supported is False


def test_language_detection():
    print("\n[TEST] Testing programming language detection...")
    cases = [
        ("test.py", "Python"),
        ("app/main.ts", "TypeScript"),
        ("styles.css", "CSS"),
        ("unknown.xyz", "Unknown")
    ]
    for path, expected in cases:
        lang = detect_language(path)
        print(f"[TEST] Path '{path}' detected as '{lang}' (Expected: '{expected}')")
        assert lang == expected