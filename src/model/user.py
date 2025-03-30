from uuid import UUID
from enum import Enum
from typing import Optional, ClassVar

from pydantic import BaseModel, Field


class User(BaseModel):
    class Type(Enum):
        PARTICULAR = "particular"
        PROFESSIONAL = "professional"
        ENTERPRISE = "enterprise"
        ADMIN = "admin"

    VERIFIED_TYPES: ClassVar[tuple[Type, ...]] = (Type.PROFESSIONAL, Type.ENTERPRISE)
    SECONDHAND_TYPES: ClassVar[tuple[Type, ...]] = (Type.PROFESSIONAL, Type.PARTICULAR)

    id_: UUID = Field(..., alias="id")
    name: str
    surname: str
    type_: Type = Field(..., alias="type")
    nif: Optional[str]  # Only PROFESSIONAL and ENTERPRISE have a `nif`
