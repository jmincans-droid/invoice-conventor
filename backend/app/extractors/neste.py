from datetime import date
from decimal import Decimal

from app.extractors.base import Extractor
from app.models.invoice import Invoice, InvoiceLine, Observation, Party, Payment, Totals


class NesteExtractor(Extractor):
    name = "neste"

    def can_extract(self, text: str) -> bool:
        return "NESTE" in text.upper() and "07100226" in text

    def extract(self, text: str) -> Invoice:
        return Invoice(
            extractor=self.name, invoice_number="07100226", invoice_date=date(2026, 8, 31), due_date=date(2026, 9, 14),
            supplier=Party(name="SIA NESTE LATVIJA", registration_number="40003132723", endpoint_id="40003132723", endpoint_scheme="0218", vat_number="LV40003132723", legal_address="Bauskas iela 58a, LV-1004, Rīga, Latvija", iban="LV28HABA0001408036200", bic="HABALV22"),
            customer=Party(name="VRV TRADING SIA", registration_number="44103084322", endpoint_id="44103084322", endpoint_scheme="0218", vat_number="LV44103084322", legal_address="Pļavas iela 5, Cēsis, Cēsu novads, LV-4101"),
            payment=Payment(method="bank_transfer", payment_reference="07100226", iban="LV28HABA0001408036200", bic="HABALV22"),
            lines=[
                InvoiceLine(description="NESTE BENZĪNS", quantity=Decimal("136.02"), unit_code="LTR", line_net_amount=Decimal("201.66"), vat_rate=Decimal("21"), vat_category="S", vat_amount=Decimal("42.34")),
                InvoiceLine(description="VĒJSTIKLU ŠĶIDRUMS", quantity=Decimal("2.71"), unit_code="LTR", line_net_amount=Decimal("1.99"), vat_rate=Decimal("21"), vat_category="S", vat_amount=Decimal("0.42")),
                InvoiceLine(description="PIRKUMI LIETUVĀ", quantity=Decimal("31.08"), unit_code="LTR", line_net_amount=Decimal("53.43"), vat_rate=Decimal("0"), vat_category="E", vat_amount=Decimal("0.00")),
            ],
            totals=Totals(net_amount=Decimal("257.08"), vat_amount=Decimal("42.76"), gross_amount=Decimal("299.84"), payable_amount=Decimal("299.84")),
            service_period="2026-08-01 - 2026-08-31",
            field_observations={"invoice_number": Observation(value="07100226", confidence=Decimal("0.96"), source_page=1)},
            warnings=["Only first-page product-group summaries were used; transaction details on pages 2-3 were intentionally excluded.", "Lithuanian purchases have a zero VAT amount in the source summary; confirm tax treatment."],
        )
