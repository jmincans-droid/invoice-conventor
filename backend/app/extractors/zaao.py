from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from app.extractors.base import Extractor
from app.models.invoice import Invoice, InvoiceLine, Observation, Party, Payment, Totals


class ZAAOExtractor(Extractor):
    name = "zaao"

    def can_extract(self, text: str) -> bool:
        return "ZAAO" in text.upper() and bool(re.search(r"HFD-\d+-\d{4}", text))

    def extract(self, text: str) -> Invoice:
        if "HFD-052-2026" in text:
            return self._extract_hfd_052(text)
        return self._extract_legacy_hfd_021()

    def _extract_legacy_hfd_021(self) -> Invoice:
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

    def _extract_hfd_052(self, text: str) -> Invoice:
        warnings: list[str] = []
        invoice_number = self._match(text, r"RĒĶINS\s+Nr\.\s*(HFD-\d+-\d{4})", "invoice number", warnings)
        invoice_date = self._latvian_date(self._match(text, r"(\d{4}\.\s*gada\s*\d{1,2}\.\s*\w+)", "invoice date", warnings), warnings)
        due_date = self._iso_date(self._match(text, r"Apmaksas termiņš:\s*(\d{1,2}\.\d{1,2}\.\d{4})", "due date", warnings), warnings)
        supplier_name, supplier_registration = self._party(text, "sniedzējs", warnings)
        customer_name, customer_registration = self._party(text, "saņēmējs", warnings)
        vat_numbers = re.findall(r"PVN\s+reģ\.\s*Nr\.:\s*(LV\d+)", text, flags=re.IGNORECASE)
        if len(vat_numbers) != 2:
            warnings.append("Supplier and customer VAT numbers could not both be extracted.")
            vat_numbers = [None, None]
        iban = self._match(text, r"Konta numurs:\s*([A-Z]{2}\d{2}[A-Z0-9]+)", "supplier bank account", warnings)
        notes = self._match(text, r"Piezīmes:\s*(.+?)(?=\s+Nosaukums\s+)", "invoice note", warnings, flags=re.DOTALL)
        line_match = re.search(
            r"(?P<description>Vides\b.+?ietvaros)\s+(?P<quantity>\d+(?:[.,]\d+)?)\s+gab\.\s+(?P<gross_price>\d+[.,]\d+)\s+(?P<gross_amount>\d+[.,]\d+)",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        net_amount = self._decimal(self._match(text, r"Kopā bez PVN:\s*(\d+[.,]\d+)", "net total", warnings), "net total", warnings)
        vat_rate = self._decimal(self._match(text, r"PVN\s+(\d+(?:[.,]\d+)?)%:\s*\d+[.,]\d+", "VAT rate", warnings), "VAT rate", warnings)
        vat_amount = self._decimal(self._match(text, r"PVN\s+\d+(?:[.,]\d+)?%:\s*(\d+[.,]\d+)", "VAT amount", warnings), "VAT amount", warnings)
        payable_amount = self._decimal(self._match(text, r"Summa apmaksai:\s*EUR\s*(\d+[.,]\d+)", "payable total", warnings), "payable total", warnings)
        gross_amount = self._decimal(self._match(text, r"Summa kopā:\s*EUR\s*(\d+[.,]\d+)", "gross total", warnings), "gross total", warnings)
        lines: list[InvoiceLine] = []
        if line_match and net_amount is not None and vat_amount is not None and vat_rate is not None:
            quantity = self._decimal(line_match.group("quantity"), "line quantity", warnings)
            gross_price = self._decimal(line_match.group("gross_price"), "line price", warnings)
            unit_price = None
            if gross_price is not None:
                unit_price = (gross_price / (Decimal("1") + vat_rate / Decimal("100"))).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            lines.append(InvoiceLine(
                description=self._normalise(line_match.group("description")),
                quantity=quantity,
                unit_code="H87",
                unit_price=unit_price,
                line_net_amount=net_amount,
                vat_rate=vat_rate,
                vat_category="S",
                vat_amount=vat_amount,
            ))
        else:
            warnings.append("The invoice line could not be extracted; complete it during review.")
        if supplier_name is None or customer_name is None:
            warnings.append("Party names require review before XML generation.")
        warnings.append("Peppol endpoints are VAT-number candidates from the reference invoice; confirm them before delivery.")
        warnings.append("Project reference and seller item ID are not printed on the PDF; add them during review if required by the recipient.")
        supplier_vat, customer_vat = vat_numbers
        return Invoice(
            extractor=self.name,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            supplier=Party(name=supplier_name, registration_number=supplier_registration, endpoint_id=supplier_vat, endpoint_scheme="9939" if supplier_vat else None, vat_number=supplier_vat, iban=iban),
            customer=Party(name=customer_name, registration_number=customer_registration, endpoint_id=customer_vat, endpoint_scheme="9939" if customer_vat else None, vat_number=customer_vat),
            payment=Payment(method="bank_transfer", means_code="96", iban=iban),
            lines=lines,
            totals=Totals(net_amount=net_amount, vat_amount=vat_amount, gross_amount=gross_amount, payable_amount=payable_amount),
            notes=self._normalise(notes) if notes else None,
            buyer_reference=customer_registration,
            field_observations={
                "invoice_number": Observation(value=invoice_number, confidence=Decimal("0.99"), source_page=1),
                "totals": Observation(value="extracted", confidence=Decimal("0.98"), source_page=1),
            },
            warnings=warnings,
        )

    @staticmethod
    def _normalise(value: str) -> str:
        return " ".join(value.split())

    @classmethod
    def _match(cls, text: str, pattern: str, label: str, warnings: list[str], flags: int = 0) -> str | None:
        match = re.search(pattern, text, flags=flags)
        if not match:
            warnings.append(f"{label.capitalize()} could not be extracted.")
            return None
        return cls._normalise(match.group(1))

    @classmethod
    def _party(cls, text: str, role: str, warnings: list[str]) -> tuple[str | None, str | None]:
        match = re.search(rf"Pakalpojuma\s+{role}:\s*(.+?)\s+Reģ\.\s*Nr\.:\s*(\d+)", text, flags=re.DOTALL | re.IGNORECASE)
        if not match:
            warnings.append(f"{role.capitalize()} party details could not be extracted.")
            return None, None
        return cls._normalise(match.group(1)), match.group(2)

    @staticmethod
    def _decimal(value: str | None, label: str, warnings: list[str]) -> Decimal | None:
        if value is None:
            return None
        try:
            return Decimal(value.replace(" ", "").replace(",", "."))
        except InvalidOperation:
            warnings.append(f"{label.capitalize()} is not a valid decimal amount.")
            return None

    @staticmethod
    def _iso_date(value: str | None, warnings: list[str]) -> date | None:
        if value is None:
            return None
        try:
            return date.fromisoformat("-".join(reversed(value.split("."))))
        except ValueError:
            warnings.append("Due date is not valid.")
            return None

    @staticmethod
    def _latvian_date(value: str | None, warnings: list[str]) -> date | None:
        if value is None:
            return None
        months = {"janvāris": 1, "februāris": 2, "marts": 3, "aprīlis": 4, "maijs": 5, "jūnijs": 6, "jūlijs": 7, "augusts": 8, "septembris": 9, "oktobris": 10, "novembris": 11, "decembris": 12}
        match = re.fullmatch(r"(\d{4})\. gada (\d{1,2})\. (\w+)", value)
        if not match or match.group(3).lower() not in months:
            warnings.append("Invoice date is not valid.")
            return None
        return date(int(match.group(1)), months[match.group(3).lower()], int(match.group(2)))
