from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Observation(BaseModel):
    """Provenance for a field whose value may need user confirmation."""

    value: str | None = None
    confidence: Decimal = Field(ge=0, le=1)
    source_page: int | None = Field(default=None, ge=1)
    warning: str | None = None


class Party(BaseModel):
    name: str | None = None
    registration_number: str | None = None
    endpoint_id: str | None = None
    endpoint_scheme: str | None = None
    vat_number: str | None = None
    legal_address: str | None = None
    delivery_address: str | None = None
    iban: str | None = None
    bic: str | None = None


class Payment(BaseModel):
    method: str | None = None
    payment_reference: str | None = None
    iban: str | None = None
    bic: str | None = None


class InvoiceLine(BaseModel):
    description: str | None = None
    quantity: Decimal | None = None
    unit_code: str | None = None
    unit_price: Decimal | None = None
    line_net_amount: Decimal | None = None
    vat_rate: Decimal | None = None
    vat_category: Literal["S", "Z", "E", "O"] | None = None
    vat_amount: Decimal | None = None


class Totals(BaseModel):
    net_amount: Decimal | None = None
    vat_amount: Decimal | None = None
    gross_amount: Decimal | None = None
    payable_amount: Decimal | None = None
    prepayments: Decimal = Decimal("0.00")


class Invoice(BaseModel):
    model_config = ConfigDict(json_encoders={Decimal: lambda value: format(value, "f")})

    invoice_number: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    currency: str | None = "EUR"
    supplier: Party = Field(default_factory=Party)
    customer: Party = Field(default_factory=Party)
    payment: Payment = Field(default_factory=Payment)
    lines: list[InvoiceLine] = Field(default_factory=list)
    totals: Totals = Field(default_factory=Totals)
    notes: str | None = None
    service_period: str | None = None
    field_observations: dict[str, Observation] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    extractor: str | None = None
