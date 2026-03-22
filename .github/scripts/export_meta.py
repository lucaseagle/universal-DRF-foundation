#!/usr/bin/env python3
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    tomllib = None


def resolve_version() -> str:
    # Tag takes precedence if present
    ref_type = os.environ.get("GITHUB_REF_TYPE")
    ref_name = os.environ.get("GITHUB_REF_NAME")
    if ref_type == "tag" and ref_name:
        return ref_name

    default = "0.0.0"
    path = Path("pyproject.toml")
    if not (tomllib and path.exists()):
        return default

    try:
        data = tomllib.load(path.open("rb"))
        return data.get("project", {}).get("version", default) or default
    except Exception:
        return default


def main() -> None:
    version = resolve_version()
    sha = os.environ.get("GITHUB_SHA", "")

    print("APP_NAME=drf-api-template")
    print(f"APP_VERSION={version}")
    print(f"COMMIT={sha[:7]}")
    print("DEBUG=false")
    print("SECRET_KEY=test-secret-key")


if __name__ == "__main__":
    main()
