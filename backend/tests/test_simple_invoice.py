from decimal import Decimal


def test_valmieras_golfa_skola_fixture(valmieras) -> None:
    assert valmieras.extractor == "valmieras_golfa_skola"
    assert valmieras.invoice_number == "VGS1"
    assert valmieras.totals.payable_amount == Decimal("1000.00")
    assert valmieras.supplier.vat_number is None
    assert valmieras.lines[0].vat_rate == Decimal("0")
