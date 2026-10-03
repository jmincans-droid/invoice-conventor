from decimal import Decimal


def test_zaao_fixture(zaao) -> None:
    assert zaao.extractor == "zaao"
    assert zaao.invoice_number == "HFD-021-2026"
    assert zaao.totals.payable_amount == Decimal("814.48")
    assert len(zaao.lines) == 3
    assert zaao.lines[1].line_net_amount == Decimal("-0.27")
