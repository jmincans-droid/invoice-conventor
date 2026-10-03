from decimal import Decimal

from app.validation.invoice_validator import validate_invoice


def test_totals_validate_for_supported_fixture(valmieras) -> None:
    assert validate_invoice(valmieras).valid


def test_invalid_total_is_reported(valmieras) -> None:
    valmieras.totals.gross_amount = Decimal("999.00")
    result = validate_invoice(valmieras)
    assert not result.valid
    assert "Net amount plus VAT amount" in result.errors[0]
