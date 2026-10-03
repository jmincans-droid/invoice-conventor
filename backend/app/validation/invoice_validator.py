from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.invoice import Invoice

TOLERANCE = Decimal("0.01")


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def validate_invoice(invoice: Invoice) -> ValidationResult:
    errors: list[str] = []
    warnings = list(invoice.warnings)
    required = {
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date,
        "supplier registration number": invoice.supplier.registration_number,
        "supplier electronic address": invoice.supplier.endpoint_id,
        "supplier electronic-address scheme": invoice.supplier.endpoint_scheme,
        "customer registration number": invoice.customer.registration_number,
        "customer electronic address": invoice.customer.endpoint_id,
        "customer electronic-address scheme": invoice.customer.endpoint_scheme,
        "currency": invoice.currency,
        "payable amount": invoice.totals.payable_amount,
    }
    for name, value in required.items():
        if value in (None, ""):
            errors.append(f"Missing required field: {name}")
    if not invoice.lines:
        errors.append("At least one invoice line is required")

    known_line_amounts = [line.line_net_amount for line in invoice.lines if line.line_net_amount is not None]
    if invoice.lines and len(known_line_amounts) != len(invoice.lines):
        warnings.append("Some line net amounts are unknown; line-total validation was skipped.")
    elif known_line_amounts and invoice.totals.net_amount is not None:
        if abs(sum(known_line_amounts) - invoice.totals.net_amount) > TOLERANCE:
            errors.append("Line net amounts do not match net total within 0.01 EUR")

    totals = invoice.totals
    if None not in (totals.net_amount, totals.vat_amount, totals.gross_amount):
        if abs(totals.net_amount + totals.vat_amount - totals.gross_amount) > TOLERANCE:
            errors.append("Net amount plus VAT amount does not match gross amount within 0.01 EUR")
    if None not in (totals.gross_amount, totals.payable_amount):
        if abs(totals.gross_amount - totals.prepayments - totals.payable_amount) > TOLERANCE:
            errors.append("Gross amount minus prepayments does not match payable amount within 0.01 EUR")
    return ValidationResult(valid=not errors, errors=errors, warnings=warnings)
