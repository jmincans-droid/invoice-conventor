from app.validation.invoice_validator import validate_invoice


def test_negative_invoice_line_is_allowed(zaao) -> None:
    assert zaao.lines[1].line_net_amount < 0
    assert validate_invoice(zaao).valid
