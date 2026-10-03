from abc import ABC, abstractmethod

from app.models.invoice import Invoice


class Extractor(ABC):
    name: str

    @abstractmethod
    def can_extract(self, text: str) -> bool: ...

    @abstractmethod
    def extract(self, text: str) -> Invoice: ...
