from typing import List, Optional
from common import constant
from pydantic import BaseModel


class SearchConditionDto(BaseModel):
    index: str
    query: Optional[List[str]] = [""]
    fields: Optional[List[str]] = ["*"]
    page: Optional[int] = 1
    limit: Optional[int] = 10
    fuzziness: Optional[str] = "AUTO"
    orderBy: Optional[str] = constant.ORDER_BY["DESC"]
    fieldVector: Optional[str] = "sentence_vector"
