#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from shutil import which

SERVER_LOG_PATH = Path(tempfile.gettempdir()) / "django-server.log"
HEALTH_URL = "http://127.0.0.1:8000/api/health/"


def _print_server_log() -> None:
    print("Server log:")
    try:
        print(SERVER_LOG_PATH.read_text(encoding="utf-8"))
    except OSError:
        print("<failed to read server log>")


def _is_server_ready(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def main() -> int:
    migrate_cmd = [sys.executable, "src/manage.py", "migrate", "--noinput"]
    server_cmd = [sys.executable, "src/manage.py", "runserver", "0.0.0.0:8000"]
    schemathesis_base_cmd = (
        ["schemathesis"]
        if which("schemathesis")
        else [sys.executable, "-m", "schemathesis.cli"]
    )
    schemathesis_cmd = [
        *schemathesis_base_cmd,
        "run",
        "openapi/schema.yaml",
        "--checks="
        "not_a_server_error,status_code_conformance,"
        "content_type_conformance,response_schema_conformance",
        "--mode=positive",
        "--include-method",
        "GET",
        "--include-path-regex=^/api/health",
        "--url=http://127.0.0.1:8000",
    ]

    print("Applying migrations...")
    migrate_result = subprocess.run(migrate_cmd, check=False)
    if migrate_result.returncode != 0:
        return migrate_result.returncode

    SERVER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Starting dev server...")
    with SERVER_LOG_PATH.open("w", encoding="utf-8") as log_file:
        server_process = subprocess.Popen(
            server_cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )

    try:
        print("Waiting for server to become ready...")
        ready = False
        for _ in range(30):
            if server_process.poll() is not None:
                print("Server process exited before readiness check completed.")
                _print_server_log()
                return 1
            if _is_server_ready(HEALTH_URL):
                ready = True
                break
            time.sleep(1)

        if not ready:
            print("Server did not become ready in time")
            _print_server_log()
            return 1

        print("Running Schemathesis...")
        result = subprocess.run(schemathesis_cmd, check=False)
        return result.returncode
    finally:
        if server_process.poll() is None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
