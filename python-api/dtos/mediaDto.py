from typing import List
from pydantic import BaseModel


class MediaDto(BaseModel):
    # constructor
    def __init__(
        self,
        id: str,
        name: str,
        dir: str,
        type: int,
        location: str,
        ext: str,
    ):

        # public data members
        self.id = id
        self.name = name
        self.dir = dir
        self.type = type
        self.location = location
        self.ext = ext