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

## Verification

From `backend`, run `./.venv/Scripts/python.exe -m pytest -q` on Windows after changes. If the environment is missing, create it with `python -m venv .venv` and install `requirements.txt`.
