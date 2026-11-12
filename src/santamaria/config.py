"""Credentials and paths. Nothing secret lives in the repository."""
from __future__ import annotations

import os
from pathlib import Path
from typing import NamedTuple

PACKAGE_DATA = Path(__file__).resolve().parents[2] / "data" / "parameters"


class Credentials(NamedTuple):
    api_key: str
    cse_id: str


def parameters_dir() -> Path:
    """Folder with the CSV parameter files: ``$SANTA_MARIA_PARAMETERS`` or ``data/parameters``."""
    return Path(os.environ.get("SANTA_MARIA_PARAMETERS", PACKAGE_DATA))


def load_credentials(csv_path=None) -> Credentials:
    """Google Custom Search credentials.

    Read from ``GOOGLE_API_KEY`` and ``GOOGLE_CSE_ID``. For the old layout, pass the path of
    an ``API_KEY.csv`` with columns ``API_KEY`` and ``CSE_ID`` (keep it out of git).
    """
    key, cse = os.environ.get("GOOGLE_API_KEY"), os.environ.get("GOOGLE_CSE_ID")
    if key and cse:
        return Credentials(key, cse)
    if csv_path is not None:
        import pandas as pd

        row = pd.read_csv(csv_path).iloc[0]
        return Credentials(str(row["API_KEY"]), str(row["CSE_ID"]))
    raise RuntimeError("Set GOOGLE_API_KEY and GOOGLE_CSE_ID, or pass the path of API_KEY.csv")
