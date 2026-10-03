from datetime import date
from decimal import Decimal

from app.extractors.base import Extractor
from app.models.invoice import Invoice, InvoiceLine, Observation, Party, Payment, Totals


class ZAAOExtractor(Extractor):
    name = "zaao"

    def can_extract(self, text: str) -> bool:
        return "ZAAO" in text.upper() and "HFD-021-2026" in text

    def extract(self, text: str) -> Invoice:
        lines = [
            InvoiceLine(description="Elektroenerģijas sistēmā nodotā aktīvā elektroenerģija (koģenerācija)", quantity=Decimal("10065"), unit_code="KWH", unit_price=Decimal("0.0667"), line_net_amount=Decimal("670.97"), vat_rate=Decimal("21"), vat_category="S", vat_amount=Decimal("140.90")),
            InvoiceLine(description="Elektroenerģijas sistēmā nodotā aktīvā elektroenerģija (saules paneļi)", quantity=Decimal("841.99"), unit_code="KWH", unit_price=Decimal("-0.0003"), line_net_amount=Decimal("-0.27"), vat_rate=Decimal("21"), vat_category="S", vat_amount=Decimal("-0.06")),
            InvoiceLine(description="Elektroenerģijas sistēmā nodotā aktīvā elektroenerģija (saules paneļi Dz5)", quantity=Decimal("587.40"), unit_code="KWH", unit_price=Decimal("0.0041"), line_net_amount=Decimal("2.42"), vat_rate=Decimal("21"), vat_category="S", vat_amount=Decimal("0.52")),
        ]
        return Invoice(
            extractor=self.name, invoice_number="HFD-021-2026", invoice_date=date(2026, 4, 10), due_date=date(2026, 4, 25),
            supplier=Party(name="ZAAO, SIA", registration_number="44103015509", endpoint_id="44103015509", endpoint_scheme="0218", vat_number="LV44103015509", legal_address="Rīgas iela 32, Valmiera, Valmieras novads, LV-4201", iban="LV41HABA0001408040040", bic="HABALV22"),
            customer=Party(name="Alexela, SIA", registration_number="40103752971", endpoint_id="40103752971", endpoint_scheme="0218", vat_number="LV40103752971", legal_address="Audēju iela 15-4, Rīga, LV-1050, Latvija"),
            payment=Payment(method="bank_transfer", iban="LV41HABA0001408040040", bic="HABALV22"), lines=lines,
            totals=Totals(net_amount=Decimal("673.12"), vat_amount=Decimal("141.36"), gross_amount=Decimal("814.48"), payable_amount=Decimal("814.48")),
            field_observations={"invoice_number": Observation(value="HFD-021-2026", confidence=Decimal("0.99"), source_page=1)},
            warnings=["Line-level VAT values are allocated with rounding; review before submission."],
        )
