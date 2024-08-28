from typing import List
from pydantic import BaseModel


class SentenceDto(BaseModel):
    id: str
    document_id: str
    page_number: int
    sentence: str
    # sentence_vector: List[float] = []
    
    def __getField__(self, field: str):
        if field and hasattr(self, field):

            return getattr(self, field)

        return None
