from typing import List
from pydantic import BaseModel


class DocumentDto(BaseModel):
    def __init__(
        self, id: str, name: str, number_of_page: int, name_vector: List[float] = []
    ):
        # public data members
        self.id = id
        self.name = name
        self.number_of_page = number_of_page
        self.name_vector = name_vector
