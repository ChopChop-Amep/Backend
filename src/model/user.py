from uuid import UUID

from pydantic import BaseModel, Field


class User(BaseModel):
    id_: UUID = Field(..., alias="id")
    name: str
    surname: str


class Particular(User):
    pass


class Professional(User):
    pass


class Enterprise(User):
    pass


class Admin(User):
    pass
