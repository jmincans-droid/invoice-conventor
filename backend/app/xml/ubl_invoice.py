import base64
from decimal import Decimal

from lxml import etree

from app.models.invoice import Invoice, InvoiceLine

CUSTOMIZATION_ID = "urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0"
PROFILE_ID = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"
NS = {"": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2", "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2", "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}


def _money(value: Decimal | None) -> str:
    return f"{(value or Decimal('0')):.2f}"


def _text(parent: etree._Element, tag: str, value: object | None, **attrs: str) -> etree._Element:
    node = etree.SubElement(parent, f"{{{NS['cbc']}}}{tag}", **attrs)
    node.text = str(value or "")
    return node


def _party(parent: etree._Element, tag: str, party) -> None:
    container = etree.SubElement(parent, f"{{{NS['cac']}}}{tag}")
    party_node = etree.SubElement(container, f"{{{NS['cac']}}}Party")
    _text(party_node, "EndpointID", party.endpoint_id, schemeID=party.endpoint_scheme or "")
    if party.registration_number:
        ident = etree.SubElement(party_node, f"{{{NS['cac']}}}PartyIdentification")
        _text(ident, "ID", party.registration_number, schemeID=party.endpoint_scheme or "")
    if party.vat_number:
        scheme = etree.SubElement(party_node, f"{{{NS['cac']}}}PartyTaxScheme")
        _text(scheme, "CompanyID", party.vat_number)
        tax = etree.SubElement(scheme, f"{{{NS['cac']}}}TaxScheme")
        _text(tax, "ID", "VAT")
    legal = etree.SubElement(party_node, f"{{{NS['cac']}}}PartyLegalEntity")
    _text(legal, "RegistrationName", party.name)
    _text(legal, "CompanyID", party.registration_number, schemeID=party.endpoint_scheme or "")
    if party.legal_address:
        address = etree.SubElement(party_node, f"{{{NS['cac']}}}PostalAddress")
        _text(address, "StreetName", party.legal_address)


def _line(parent: etree._Element, index: int, line: InvoiceLine, currency: str) -> None:
    node = etree.SubElement(parent, f"{{{NS['cac']}}}InvoiceLine")
    _text(node, "ID", index)
    _text(node, "InvoicedQuantity", line.quantity, unitCode=line.unit_code or "C62")
    _text(node, "LineExtensionAmount", _money(line.line_net_amount), currencyID=currency)
    item = etree.SubElement(node, f"{{{NS['cac']}}}Item")
    _text(item, "Name", line.description)
    tax = etree.SubElement(item, f"{{{NS['cac']}}}ClassifiedTaxCategory")
    _text(tax, "ID", line.vat_category or "S")
    _text(tax, "Percent", line.vat_rate or Decimal("0"))
    scheme = etree.SubElement(tax, f"{{{NS['cac']}}}TaxScheme")
    _text(scheme, "ID", "VAT")
    if line.unit_price is not None:
        price = etree.SubElement(node, f"{{{NS['cac']}}}Price")
        _text(price, "PriceAmount", _money(line.unit_price), currencyID=currency)


def generate_ubl_invoice(
    invoice: Invoice, *, supporting_pdf: bytes | None = None, supporting_pdf_filename: str | None = None
) -> bytes:
    root = etree.Element(f"{{{NS['']}}}Invoice", nsmap={None: NS[""], "cac": NS["cac"], "cbc": NS["cbc"]})
    currency = invoice.currency or "EUR"
    _text(root, "CustomizationID", CUSTOMIZATION_ID)
    _text(root, "ProfileID", PROFILE_ID)
    _text(root, "ID", invoice.invoice_number)
    _text(root, "IssueDate", invoice.invoice_date)
    if invoice.due_date:
        _text(root, "DueDate", invoice.due_date)
    _text(root, "InvoiceTypeCode", "380")
    _text(root, "DocumentCurrencyCode", currency)
    if supporting_pdf is not None:
        reference = etree.SubElement(root, f"{{{NS['cac']}}}AdditionalDocumentReference")
        _text(reference, "ID", "original-invoice-pdf")
        _text(reference, "DocumentDescription", "Original invoice PDF")
        attachment = etree.SubElement(reference, f"{{{NS['cac']}}}Attachment")
        binary = etree.SubElement(attachment, f"{{{NS['cbc']}}}EmbeddedDocumentBinaryObject", mimeCode="application/pdf", filename=supporting_pdf_filename or "original-invoice.pdf")
        binary.text = base64.b64encode(supporting_pdf).decode("ascii")
    _party(root, "AccountingSupplierParty", invoice.supplier)
    _party(root, "AccountingCustomerParty", invoice.customer)
    if invoice.payment.method:
        means = etree.SubElement(root, f"{{{NS['cac']}}}PaymentMeans")
        _text(means, "PaymentMeansCode", "30" if invoice.payment.method == "bank_transfer" else invoice.payment.method)
        if invoice.payment.payment_reference:
            _text(means, "InstructionID", invoice.payment.payment_reference)
        if invoice.payment.iban:
            account = etree.SubElement(means, f"{{{NS['cac']}}}PayeeFinancialAccount")
            _text(account, "ID", invoice.payment.iban)
    tax_total = etree.SubElement(root, f"{{{NS['cac']}}}TaxTotal")
    _text(tax_total, "TaxAmount", _money(invoice.totals.vat_amount), currencyID=currency)
    total = etree.SubElement(root, f"{{{NS['cac']}}}LegalMonetaryTotal")
    _text(total, "LineExtensionAmount", _money(invoice.totals.net_amount), currencyID=currency)
    _text(total, "TaxExclusiveAmount", _money(invoice.totals.net_amount), currencyID=currency)
    _text(total, "TaxInclusiveAmount", _money(invoice.totals.gross_amount), currencyID=currency)
    _text(total, "PrepaidAmount", _money(invoice.totals.prepayments), currencyID=currency)
    _text(total, "PayableAmount", _money(invoice.totals.payable_amount), currencyID=currency)
    for index, line in enumerate(invoice.lines, 1):
        _line(root, index, line, currency)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)
