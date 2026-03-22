from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppPaths:
    project_root: Path
    data_dir: Path
    db_path: Path
    images_dir: Path
    backups_dir: Path


def _windows_default_project() -> Path:
    return Path(r"C:\Users\lopes\Downloads\Squackts")


def get_paths() -> AppPaths:
    project_root = Path(os.getenv("SQUACKTS_PROJECT_ROOT", str(_windows_default_project()))).expanduser()
    local_appdata = Path(os.getenv("LOCALAPPDATA", str(project_root / "localappdata")))
    data_dir = Path(os.getenv("SQUACKTS_DATA_DIR", str(local_appdata / "SquackTS_Enterprise" / "data")))
    db_path = Path(os.getenv("SQUACKTS_DB_PATH", str(data_dir / "squackts_enterprise.db")))
    images_dir = Path(os.getenv("SQUACKTS_IMAGES_DIR", str(project_root / "images")))
    backups_dir = Path(os.getenv("SQUACKTS_BACKUPS_DIR", str(project_root / "backups")))
    return AppPaths(project_root, data_dir, db_path, images_dir, backups_dir)
