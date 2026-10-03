# PDF -> E-Rēķins

MVP that extracts supported Latvian invoice PDFs into a reviewed, structured invoice and generates UBL 2.1 / Peppol BIS Billing 3.0-oriented XML. No database is used.

## Codex project setup

This is a standalone Git project. `AGENTS.md` contains durable agent instructions and `.agents/skills/invoice-converter/` provides the project-specific Codex skill. Open this folder as the primary local project folder so Codex discovers both automatically.

Architecture: `PDF -> extractor -> Invoice (Pydantic + Decimal) -> user review -> business validation -> lxml UBL -> XML well-formedness check`.

## Quick start

```powershell
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

Open `http://127.0.0.1:8000` for the review UI. The health check is at `GET /health`.

## API

- `POST /api/invoices/extract` - multipart field `file`; returns the reviewable Invoice JSON.
- `POST /api/invoices/validate` - Invoice JSON; returns `valid`, `errors`, and `warnings`.
- `POST /api/invoices/xml` - Invoice JSON; returns an XML attachment only when business validation succeeds.
- `POST /api/invoices/xml-with-pdf` - multipart `invoice_json` plus the original PDF; embeds the PDF as a Base64 UBL supporting-document attachment.

The vendor-specific extractors currently support Valmieras Golfa skola, ZAAO, and Neste Latvija. An unknown layout uses the generic extractor and returns an empty draft plus a warning rather than fabricated data. All monetary values are `Decimal` in Python.

For Latvian suppliers and customers, the supported extractors populate the electronic-address candidate from the registration number using Peppol scheme `0218` (LV:URN). Before network delivery, confirm that the recipient is registered under this exact Peppol participant ID; edit `customer.endpoint_id` and `customer.endpoint_scheme` in the review data if their provider specifies another identifier.

## Privacy and security

Uploads are PDF-only, capped at 20 MB, processed in a temporary file, then deleted. The application does not persist invoices or log full invoice text, full IBANs, or full registration numbers.

The included PDFs are supplied test fixtures. Do not use production invoices as fixtures without appropriate authorization.

## Known limitations and roadmap

This is an MVP, not a certified Peppol endpoint or a complete EN 16931 validator. It checks XML well-formedness and deliberately has a TODO insertion point for official Peppol XSD/Schematron validation. It has no OCR for scanned PDFs, no AI-assisted generic extraction, no VID API integration, no batch processing, and no audit trail/accounts.

The review UI's XML button creates the attachment variant. The supplied PDF exists only during that request; Base64 embedding increases the XML size by roughly one third.

Planned phases: OCR; AI-assisted generic extraction; full Peppol validation; VID E-Invoice API; batch processing; audit trail and user accounts.
