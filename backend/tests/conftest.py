from pathlib import Path

import pytest

from app.services.extraction_service import extract_invoice


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valmieras(fixtures_dir):
    return extract_invoice(fixtures_dir / "valmieras-golfa-skola.pdf")


@pytest.fixture
def zaao(fixtures_dir):
    return extract_invoice(fixtures_dir / "zaao.pdf")


@pytest.fixture
def neste(fixtures_dir):
    return extract_invoice(fixtures_dir / "neste.pdf")
