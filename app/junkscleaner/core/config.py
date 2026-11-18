"""Persistent application configuration management."""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """User preferences and application state configuration."""

    version: int = 1
    theme: str = "dark"  # "dark" or "light"
    monitoring_interval_seconds: float = 2.0
    confirm_before_clean: bool = True
    max_history_records: int = 100

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        return cls(
            version=int(data.get("version", 1)),
            theme=str(data.get("theme", "dark")),
            monitoring_interval_seconds=float(data.get("monitoring_interval_seconds", 2.0)),
            confirm_before_clean=bool(data.get("confirm_before_clean", True)),
            max_history_records=int(data.get("max_history_records", 100)),
        )


def get_default_config_path() -> Path:
    """Return standard user config file path."""
    import sys

    if sys.platform == "win32":
        import os

        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        import os

        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    config_dir = base / "JunksCleaner"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


class ConfigManager:
    """Thread-safe configuration loader and saver."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or get_default_config_path()
        self.config = self.load()

    def load(self) -> AppConfig:
        """Load configuration from disk with corrupt-file fallback."""
        if not self.config_path.exists():
            return AppConfig()

        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = json.load(f)
            return AppConfig.from_dict(data)
        except Exception as e:
            logger.warning(
                "Failed to load config from %s: %s; using defaults.", self.config_path, e
            )
            return AppConfig()

    def save(self) -> bool:
        """Save current configuration to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error("Failed to save config to %s: %s", self.config_path, e)
            return False
