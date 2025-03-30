from uuid import UUID
from enum import Enum
from typing import Optional, ClassVar

from pydantic import BaseModel, Field


class User(BaseModel):
    id_: UUID = Field(..., alias="id")
    name: str
    surname: str

class Particular(User):
    def whatever():
        print("hi")

class Professional(User):
    def whatever():
        print("hi")

class Enterprise(User):
    def whatever():
        print("hi")

class Admin(User):
    def whatever():
        print("hi")
