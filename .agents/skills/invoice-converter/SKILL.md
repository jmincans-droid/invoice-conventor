---
name: invoice-converter
description: "Build or maintain the Latvian PDF-to-Peppol invoice converter, including extraction, review, validation, UBL XML, and supported vendor parsers."
---

# Invoice Converter

Use this skill for work on this repository's invoice-conversion workflow.

- Preserve the review step: source PDFs are not authoritative structured data.
- Keep money as `Decimal`; validate totals deterministically before generating XML.
- Add or change vendor parsers only with fixtures and tests that cover the actual expected fields and totals.
- Treat recipient Peppol endpoint identifiers as candidates unless verified by the recipient or its service provider.
- Do not add invoice persistence, broad logging, or delivery to external endpoints without explicit user authorization.
- Run the backend pytest suite after changes.
- For ZAAO HFD invoice layouts with VAT-inclusive unit prices, calculate the UBL net unit price from the parsed VAT rate and retain its meaningful decimal precision. Require the resulting line and total amounts to validate within 0.01 EUR.
- Generate one `cac:TaxSubtotal` per VAT category, in addition to `cac:TaxTotal`. Do not fabricate project references, delivery locations, seller item IDs, or Peppol endpoint registrations when they are not evidenced by the source PDF; surface them for review instead.
