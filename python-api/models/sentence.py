from typing import Optional

from sqlmodel import Field, SQLModel
import uuid

class Sentence(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    document_id: str 
    page_number: int
    sentence: Optional[str] = Field(default="")