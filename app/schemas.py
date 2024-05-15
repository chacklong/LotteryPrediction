# schemas.py
from pydantic import BaseModel

class FetchParams(BaseModel):
    url: str
    params: str