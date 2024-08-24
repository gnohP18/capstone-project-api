from typing import List
from pydantic import BaseModel


class SentenceDto(BaseModel):
    # constructor
    def __init__(
        self,
        id: str,
        document_id: str,
        name: str,
        page_number: int,
        sentence: str,
        sentence_vector: List[float] = [],
    ):

        # public data members
        self.id = id
        self.document_id = document_id
        self.name = name
        self.page_number = page_number
        self.sentence = sentence
        self.sentence_vector = sentence_vector
