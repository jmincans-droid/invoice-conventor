from decimal import Decimal

from app.extractors.zaao import ZAAOExtractor
from app.validation.invoice_validator import validate_invoice


def test_hfd_052_parser_extracts_reviewable_invoice() -> None:
    text = """
    RĒĶINS Nr. HFD-052-2026
    2026. gada 2. oktobris
    Pakalpojuma sniedzējs: Piegādātājs, SIA Reģ. Nr.: 40000000001
    PVN reģ. Nr.: LV40000000001
    Konta numurs: LV00BANK0000000000000
    Pakalpojuma saņēmējs: Saņēmējs, SIA Reģ. Nr.: 40000000002
    PVN reģ. Nr.: LV40000000002
    Piezīmes: Pārskatāma piezīme
    Apmaksas termiņš: 16.10.2026
    Nosaukums Daudzums Mērv. Cena Summa
    Vides izglītības nodarbības projekta ietvaros 23 gab. 3.00 69.00
    Kopā bez PVN: 57.02
    PVN 21%: 11.98
    Summa kopā: EUR 69.00
    Summa apmaksai: EUR 69.00
    """

    invoice = ZAAOExtractor().extract(text)

    assert invoice.invoice_number == "HFD-052-2026"
    assert invoice.payment.means_code == "96"
    assert invoice.supplier.endpoint_scheme == "9939"
    assert invoice.customer.endpoint_scheme == "9939"
    assert len(invoice.lines) == 1
    assert invoice.lines[0].unit_code == "H87"
    assert invoice.lines[0].unit_price == Decimal("2.479339")
    assert invoice.totals.payable_amount == Decimal("69.00")
    assert validate_invoice(invoice).valid
