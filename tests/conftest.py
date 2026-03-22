import os
import tempfile
from pathlib import Path

_tmpdir = Path(__file__).resolve().parent / ".tmp"
_tmpdir.mkdir(exist_ok=True)
os.environ.setdefault("TMPDIR", str(_tmpdir))
tempfile.tempdir = str(_tmpdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Default to SQLite for local test runs unless explicitly disabled.
if os.getenv("USE_SQLITE_FOR_TESTS", "true").lower() == "true":
    os.environ["DATABASE_ENGINE"] = "django.db.backends.sqlite3"
    os.environ["DATABASE_NAME"] = str(_tmpdir / "test_db.sqlite3")
