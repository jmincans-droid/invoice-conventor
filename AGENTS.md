# Invoice Converter Peppol

## Purpose

Maintain the Latvian PDF-to-e-invoice MVP in this repository. Its required path is PDF extraction -> reviewable `Invoice` model -> deterministic validation -> UBL XML. Do not generate UBL directly from raw PDF text.

## Working rules

- Treat extracted values as uncertain unless supported by a parser; return `null`, a warning, and confidence rather than guessing.
- Keep financial calculations in `Decimal` and preserve the 0.01 EUR validation tolerance.
- Do not persist uploaded invoices. Do not log full PDF text, IBANs, registration numbers, or other full invoice contents.
- Keep the 20 MB PDF-only upload restriction.
- A Peppol endpoint candidate is not proof that the recipient is registered. Keep it editable and require confirmation before delivery integrations.
- Use `lxml`; do not construct XML via string concatenation.
- For supported ZAAO HFD invoices, derive the net unit price from a VAT-inclusive printed price only when the parsed line total and VAT total validate within 0.01 EUR. Preserve the calculated price precision in UBL; do not force it to two decimal places.
- Emit a `cac:TaxSubtotal` for every supported VAT category. Values such as project references, delivery locations and seller item IDs that are absent from the PDF must remain empty with a review warning, rather than being inferred from a comparison XML.
- A VAT-based electronic address with scheme `9939` is still a recipient endpoint candidate and must remain editable for confirmation.

## Verification

From `backend`, run `./.venv/Scripts/python.exe -m pytest -q` on Windows after changes. If the environment is missing, create it with `python -m venv .venv` and install `requirements.txt`.
