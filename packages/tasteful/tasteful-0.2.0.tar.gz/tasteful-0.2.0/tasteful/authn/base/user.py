from pydantic import BaseModel


class BaseUser(BaseModel):
    name: str
