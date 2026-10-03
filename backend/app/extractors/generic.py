from app.extractors.base import Extractor
from app.models.invoice import Invoice


class GenericExtractor(Extractor):
    name = "generic"

    def can_extract(self, text: str) -> bool:
        return True

    def extract(self, text: str) -> Invoice:
        return Invoice(
            extractor=self.name,
            warnings=[
                "No vendor-specific extractor matched. No financial values were inferred; review and complete the form."
            ],
        )
