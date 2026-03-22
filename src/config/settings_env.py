import os
import subprocess
import tomllib
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


def _default_app_version() -> str:
    if os.getenv("GITHUB_REF_TYPE") == "tag":
        ref_name = os.getenv("GITHUB_REF_NAME")
        if ref_name:
            return ref_name

    pyproject_path = BASE_DIR.parent / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with pyproject_path.open("rb") as pyproject:
                contents = tomllib.load(pyproject)
        except (OSError, tomllib.TOMLDecodeError):
            return "0.0.0"

        version = contents.get("project", {}).get("version")
        if version:
            return str(version)

    return "0.0.0"


def _default_commit() -> str:
    github_sha = os.getenv("GITHUB_SHA")
    if github_sha:
        return github_sha[:7]

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=BASE_DIR.parent,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"

    return result.stdout.strip() or "unknown"


class AppSettings(BaseSettings):
    secret_key: str = Field(default="dev-secret-key", alias="SECRET_KEY")
    debug: bool = Field(default=True, alias="DEBUG")
    allowed_hosts: list[str] = Field(default_factory=lambda: ["*"])
    time_zone: str = Field(default="Europe/Warsaw", alias="TIME_ZONE")
    service: str = Field(default="drf-api-template", alias="APP_NAME")
    version: str = Field(default_factory=_default_app_version, alias="APP_VERSION")
    commit: str = Field(default_factory=_default_commit, alias="COMMIT")
    api_readonly: bool = Field(default=True, alias="API_READONLY")
    default_user_id: str = Field(
        default="00000000-0000-0000-0000-000000000000", alias="DEFAULT_USER_ID"
    )
    use_sqlite_for_tests: bool = Field(default=True, alias="USE_SQLITE_FOR_TESTS")
    database_engine: str = "django.db.backends.sqlite3"
    database_name: str = str(BASE_DIR / "db.sqlite3")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    @property
    def database_config(self) -> dict:
        if self.use_sqlite_for_tests:
            return {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": self.database_name,
            }

        return {
            "ENGINE": self.database_engine,
            "NAME": self.database_name,
        }
