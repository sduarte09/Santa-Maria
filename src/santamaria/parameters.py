"""Water-body, newspaper and keyword tables."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, NamedTuple, Sequence

import pandas as pd

from .config import parameters_dir


class Parameters(NamedTuple):
    rivers: pd.DataFrame
    reservoirs: pd.DataFrame
    municipalities: pd.DataFrame
    keywords: pd.DataFrame
    newspapers: pd.DataFrame


def _read(folder: Path, name: str) -> pd.DataFrame:
    frame = pd.read_csv(folder / name, encoding="utf-8-sig")
    return frame.loc[:, ~frame.columns.str.startswith("Unnamed")]  # trailing comma columns


def load_parameters(folder=None) -> Parameters:
    folder = Path(folder) if folder is not None else parameters_dir()
    return Parameters(
        rivers=_read(folder, "Rivers.csv"),
        reservoirs=_read(folder, "Reservoirs.csv"),
        municipalities=_read(folder, "Municipalities.csv"),
        keywords=_read(folder, "Key_Words.csv"),
        newspapers=_read(folder, "Newspapers.csv"),
    )


def merge_duplicate_elements(table: pd.DataFrame) -> pd.DataFrame:
    """One row per ``Element``; the department strings of its duplicates are concatenated.

    Rivers and reservoirs appear several times (one row per segment). The first row is kept
    and ``DPTO`` collects the departments of all rows, as in the original scripts.
    """
    first = table.drop_duplicates(subset="Element").reset_index(drop=True)
    joined = table.groupby("Element", sort=False)["DPTO"].apply("".join)
    first["DPTO"] = first["Element"].map(joined)
    return first


def split_departments(joined: str, known: Sequence[str]) -> List[str]:
    """Departments in a string such as ``'RISARALDATOLIMATOLIMA'``, without repeats.

    The files store department names glued together. Matching is greedy on the longest known
    name first, so ``NORTE DE SANTANDER`` is not also read as ``SANTANDER``.
    """
    names = sorted({k for k in known}, key=len, reverse=True)
    if not names:
        return []
    found = re.findall("|".join(re.escape(n) for n in names), joined or "")
    return list(dict.fromkeys(found))


def newspapers_for(departments: str, newspapers: pd.DataFrame) -> pd.DataFrame:
    """National papers (``Extension == 'ALL'``) plus the regional papers of the departments."""
    regional = newspapers.loc[newspapers["Extension"] != "ALL", "Extension"].unique()
    wanted = set(split_departments(departments, regional))
    keep = (newspapers["Extension"] == "ALL") | newspapers["Extension"].isin(wanted)
    return newspapers[keep].reset_index(drop=True)


def topics_of(keywords: pd.DataFrame, column: str = "Water") -> List[str]:
    """Non-empty keywords of one column (``Water``, ``City`` or ``Social``)."""
    return [str(k) for k in keywords[column].dropna()]
