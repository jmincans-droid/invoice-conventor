from fastapi.testclient import TestClient

from app.main import app


def test_review_ui_has_original_invoice_preview() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert 'id="preview" class="pdf-preview"' in response.text
    assert "Oriģinālais rēķins" in response.text
    assert "Saņēmēja Peppol ID kandidāts" in (TestClient(app).get("/static/app.js").text)
