from typing import List
from pydantic import BaseModel

class DocumentDto(BaseModel):
    id: str
    document_id: str
    name: str
    page: int
    sentence: str
    sentence_vector: List[float] = []
