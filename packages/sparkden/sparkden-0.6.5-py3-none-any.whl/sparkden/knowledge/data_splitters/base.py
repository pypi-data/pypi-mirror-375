from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sparkden.models.knowledge import DataChunk, ParseResult


class BaseDataSplitter(ABC):
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    async def split(self, data: "ParseResult") -> list["DataChunk"]:
        pass
