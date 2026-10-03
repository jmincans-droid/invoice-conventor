from fastapi.testclient import TestClient

from app.main import app


def test_extract_and_generate_xml(fixtures_dir) -> None:
    client = TestClient(app)
    with (fixtures_dir / "valmieras-golfa-skola.pdf").open("rb") as stream:
        response = client.post("/api/invoices/extract", files={"file": ("invoice.pdf", stream, "application/pdf")})
    assert response.status_code == 200
    invoice = response.json()
    assert invoice["invoice_number"] == "VGS1"
    assert client.post("/api/invoices/validate", json=invoice).json()["valid"] is True
    xml = client.post("/api/invoices/xml", json=invoice)
    assert xml.status_code == 200
    assert xml.headers["content-type"].startswith("application/xml")


def test_rejects_non_pdf() -> None:
    response = TestClient(app).post("/api/invoices/extract", files={"file": ("nope.txt", b"nope", "text/plain")})
    assert response.status_code == 415


def test_pdf_preview_renders_page_image(fixtures_dir) -> None:
    client = TestClient(app)
    with (fixtures_dir / "valmieras-golfa-skola.pdf").open("rb") as stream:
        response = client.post("/api/invoices/preview", files={"file": ("invoice.pdf", stream, "application/pdf")})
    assert response.status_code == 200
    assert response.json()["pages"][0].startswith("data:image/png;base64,")


def test_xml_with_original_pdf_embeds_base64_attachment(fixtures_dir) -> None:
    client = TestClient(app)
    with (fixtures_dir / "valmieras-golfa-skola.pdf").open("rb") as stream:
        extracted = client.post("/api/invoices/extract", files={"file": ("invoice.pdf", stream, "application/pdf")})
    with (fixtures_dir / "valmieras-golfa-skola.pdf").open("rb") as stream:
        response = client.post("/api/invoices/xml-with-pdf", data={"invoice_json": extracted.text}, files={"file": ("original.pdf", stream, "application/pdf")})
    assert response.status_code == 200
    assert b'EmbeddedDocumentBinaryObject mimeCode="application/pdf" filename="original.pdf"' in response.content
    assert b'JVBERi0' in response.content
