from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Category(Enum):
    ARTESANAL = "artesanal"
    ANTIGUITATS = "antiguitats"
    COSMETICA = "cosmetica"
    CUINA = "cuina"
    ELECTRODOMESTICS = "electrodomestics"
    ELECTRONICA = "electronica"
    EQUIPAMENT_LAB = "equipament_lab"
    ESPORTS = "esports"
    FERRAMENTES = "ferramentes"
    INFANTIL = "infantil"
    INSTRUMENTS = "instruments"
    JARDINERIA = "jardineria"
    JOCS_DE_TAULA = "jocs_de_taula"
    JOIES_COMPLEMENTS_ACCESSORIS = "joies_complements_accessoris"
    LLIBRES = "llibres"
    MASCOTES = "mascotes"
    MOBLES = "mobles"
    NETEJA = "neteja"
    ROBA = "roba"
    SABATES = "sabates"
    VEHICLES = "vehicles"
    VIDEOJOCS = "videojocs"

    ALTRES = "altres"


class ProductType(Enum):
    VERIFIED = "verified"
    SECONDHAND = "secondhand"


# Optional fields only populated when _type == VERIFIED
class Product(BaseModel):
    type_: ProductType = Field(..., alias="type")
    id_: UUID = Field(..., alias="id")
    owner: UUID
    sku: Optional[str]
    name: str
    description: str
    stock: Optional[int]
    price: float
    image: str
    category: Category
    sold: Optional[int]


# Used to seralize the recieved json for the POST request on /product
class NewProduct(BaseModel):
    type_: ProductType = Field(..., alias="type")
    sku: Optional[str]
    name: str
    description: str
    stock: Optional[int]
    price: float
    image: str
    category: Category
