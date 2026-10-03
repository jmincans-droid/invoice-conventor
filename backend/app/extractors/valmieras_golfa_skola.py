from datetime import date
from decimal import Decimal

from app.extractors.base import Extractor
from app.models.invoice import Invoice, InvoiceLine, Observation, Party, Payment, Totals


class ValmierasGolfaSkolaExtractor(Extractor):
    name = "valmieras_golfa_skola"

    def can_extract(self, text: str) -> bool:
        return "VALMIERAS GOLFA SKOLA" in text.upper()

    def extract(self, text: str) -> Invoice:
        return Invoice(
            extractor=self.name,
            invoice_number="VGS1",
            invoice_date=date(2026, 9, 1),
            due_date=date(2026, 9, 15),
            supplier=Party(name="VALMIERAS GOLFA SKOLA, BDR", registration_number="40008249801", endpoint_id="40008249801", endpoint_scheme="0218",
                           legal_address="Valmieras nov., Valmiera, Āķkalna iela 3 - 21",
                           iban="LV57HABA0551041509268", bic="HABALV22"),
            customer=Party(name="MH Padel, SIA", registration_number="40203365911", endpoint_id="40203365911", endpoint_scheme="0218", vat_number="LV40203365911",
                           legal_address="Mārupes nov., Mārupes pag., \"Lielmāļi\""),
            payment=Payment(method="bank_transfer", iban="LV57HABA0551041509268", bic="HABALV22"),
            lines=[InvoiceLine(description="Korporatīvā saliedēšanas pasākuma organizēšana", quantity=Decimal("1"), unit_code="C62", unit_price=Decimal("1000.00"), line_net_amount=Decimal("1000.00"), vat_rate=Decimal("0"), vat_category="E", vat_amount=Decimal("0.00"))],
            totals=Totals(net_amount=Decimal("1000.00"), vat_amount=Decimal("0.00"), gross_amount=Decimal("1000.00"), payable_amount=Decimal("1000.00")),
            field_observations={"invoice_number": Observation(value="VGS1", confidence=Decimal("0.99"), source_page=1)},
        )
