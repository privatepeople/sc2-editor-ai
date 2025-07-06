# Third-party Library imports
from pydantic import BaseModel


# Pydantic models
class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: bytes
