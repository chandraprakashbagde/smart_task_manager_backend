from pydantic import BaseModel

class Error(BaseModel):
    field: str
    message: str