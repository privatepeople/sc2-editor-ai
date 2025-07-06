# Python Standard Library imports
from typing import Optional

# Third-party Library imports
from pydantic import BaseModel


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
