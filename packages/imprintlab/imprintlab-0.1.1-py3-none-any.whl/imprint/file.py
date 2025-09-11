from pydantic import BaseModel
from typing import Optional

class File(BaseModel):
    file_name: str
    file_content: bytes
    file_length: Optional[int] = 0
