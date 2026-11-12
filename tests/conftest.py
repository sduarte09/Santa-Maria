import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

DATA = Path(__file__).resolve().parents[1] / "data" / "parameters"


@pytest.fixture(scope="session")
def params():
    from santamaria.parameters import load_parameters

    return load_parameters(DATA)
