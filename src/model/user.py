from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class User(BaseModel):
    class Type(Enum):
        PARTICULAR = "particular"
        PROFESSIONAL = "professional"
        ENTERPRISE = "enterprise"
        ADMIN = "admin"

    id_: UUID = Field(..., alias="id")
    name: str
    surname: str


class Particular(User):
    pass


class Professional(User):
    nif: str


class Enterprise(User):
    nif: str


class Admin(User):
    pass
