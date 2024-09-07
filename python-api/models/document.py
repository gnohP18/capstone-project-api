from typing import Optional

from sqlmodel import Field, SQLModel

class Document(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    file_name: str
    number_of_page: int
    type_doc: str