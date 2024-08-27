from typing import List
from pydantic import BaseModel


class DocumentDto(BaseModel):
    id: str 
    name: str
    file_name: str
    number_of_page: int
    type_doc: str
    # name_vector: List[float] = []