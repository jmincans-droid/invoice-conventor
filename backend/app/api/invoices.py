import os
import tempfile
import base64
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
import pdfplumber

from app.models.invoice import Invoice
from app.services.extraction_service import extract_invoice
from app.validation.invoice_validator import validate_invoice
from app.validation.ubl_validator import validate_ubl_xml
from app.xml.ubl_invoice import generate_ubl_invoice

router = APIRouter(prefix="/api/invoices", tags=["invoices"])
MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_PREVIEW_PAGES = 10


async def _temporary_pdf(upload: UploadFile) -> Path:
    if upload.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=415, detail="Only PDF uploads are accepted")
    content = await upload.read(MAX_PDF_BYTES + 1)
    if len(content) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF must not exceed 20 MB")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=415, detail="File does not have a valid PDF signature")
    handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        handle.write(content)
        return Path(handle.name)
    finally:
        handle.close()


@router.post("/extract", response_model=Invoice)
async def extract(file: UploadFile = File(...)) -> Invoice:
    path = await _temporary_pdf(file)
    try:
        return extract_invoice(path)
    except HTTPException:
        raise
    except Exception as exc:
        # Do not include invoice contents or file path in the response/log.
        raise HTTPException(status_code=422, detail="PDF could not be processed") from exc
    finally:
        os.unlink(path)


@router.post("/preview")
async def preview(file: UploadFile = File(...)) -> dict[str, list[str] | bool]:
    """Render a short-lived visual preview; PDF bytes and page images are never stored."""
    path = await _temporary_pdf(file)
    try:
        with pdfplumber.open(path) as document:
            pages: list[str] = []
            for page in document.pages[:MAX_PREVIEW_PAGES]:
                image = page.to_image(resolution=130).original
                buffer = BytesIO()
                image.save(buffer, format="PNG", optimize=True)
                pages.append("data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii"))
            return {"pages": pages, "truncated": len(document.pages) > MAX_PREVIEW_PAGES}
    except Exception as exc:
        raise HTTPException(status_code=422, detail="PDF preview could not be rendered") from exc
    finally:
        os.unlink(path)


@router.post("/validate")
def validate(invoice: Invoice):
    return validate_invoice(invoice)


@router.post("/xml")
def xml(invoice: Invoice) -> Response:
    business = validate_invoice(invoice)
    if not business.valid:
        raise HTTPException(status_code=422, detail=business.model_dump())
    document = generate_ubl_invoice(invoice)
    errors = validate_ubl_xml(document)
    if errors:
        raise HTTPException(status_code=422, detail={"errors": errors})
    filename = f"invoice-{invoice.invoice_number or 'draft'}.xml"
    return Response(document, media_type="application/xml", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.post("/xml-with-pdf")
async def xml_with_pdf(invoice_json: str = Form(...), file: UploadFile = File(...)) -> Response:
    """Embed the original PDF as a temporary Peppol supporting-document attachment."""
    try:
        invoice = Invoice.model_validate_json(invoice_json)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invoice JSON is invalid") from exc
    business = validate_invoice(invoice)
    if not business.valid:
        raise HTTPException(status_code=422, detail=business.model_dump())
    path = await _temporary_pdf(file)
    try:
        document = generate_ubl_invoice(invoice, supporting_pdf=path.read_bytes(), supporting_pdf_filename=Path(file.filename or "original-invoice.pdf").name)
        errors = validate_ubl_xml(document)
        if errors:
            raise HTTPException(status_code=422, detail={"errors": errors})
        filename = f"invoice-{invoice.invoice_number or 'draft'}-with-pdf.xml"
        return Response(document, media_type="application/xml", headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    finally:
        os.unlink(path)
