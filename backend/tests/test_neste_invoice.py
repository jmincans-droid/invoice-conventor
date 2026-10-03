from decimal import Decimal


def test_neste_uses_summary_lines_only(neste) -> None:
    assert neste.extractor == "neste"
    assert neste.totals.payable_amount == Decimal("299.84")
    assert [line.description for line in neste.lines] == ["NESTE BENZĪNS", "VĒJSTIKLU ŠĶIDRUMS", "PIRKUMI LIETUVĀ"]
    assert "transaction details" in neste.warnings[0]
