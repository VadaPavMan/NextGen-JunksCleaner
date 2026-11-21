"""Asset path resolver for JunksCleaner."""

from pathlib import Path


def get_asset_path(filename: str) -> str:
    """Resolve an asset file path across project development and package installs."""
    # 1. Package resources / assets
    pkg_path = Path(__file__).resolve().parent / "assets" / filename
    if pkg_path.exists():
        return str(pkg_path)

    # 2. Project root / assets
    root_path = Path(__file__).resolve().parents[3] / "assets" / filename
    if root_path.exists():
        return str(root_path)

    # 3. Fallback to current working directory
    cwd_path = Path.cwd() / "assets" / filename
    if cwd_path.exists():
        return str(cwd_path)

    return str(pkg_path)
