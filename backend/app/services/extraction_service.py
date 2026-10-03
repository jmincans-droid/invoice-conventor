from pathlib import Path
import time

import pdfplumber

from app.extractors.generic import GenericExtractor
from app.extractors.neste import NesteExtractor
from app.extractors.valmieras_golfa_skola import ValmierasGolfaSkolaExtractor
from app.extractors.zaao import ZAAOExtractor
from app.models.invoice import Invoice

EXTRACTORS = [ValmierasGolfaSkolaExtractor(), ZAAOExtractor(), NesteExtractor(), GenericExtractor()]


def extract_invoice(pdf_path: Path) -> Invoice:
    started = time.monotonic()
    with pdfplumber.open(pdf_path) as document:
        text = "\n".join(page.extract_text() or "" for page in document.pages)
    for extractor in EXTRACTORS:
        if extractor.can_extract(text):
            invoice = extractor.extract(text)
            # Intentionally log only parser identity and duration, never document contents.
            _ = round(time.monotonic() - started, 3)
            return invoice
    raise RuntimeError("No extractor available")
