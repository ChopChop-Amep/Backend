from uuid import UUID
from enum import Enum

from pydantic import BaseModel


class Cathegory(Enum):
    ARTESANAL = "ARTESANAL"
    ANTIGUITATS = "ANTIGUITATS"
    COSMETICA = "COSMETICA"
    CUINA = "CUINA"
    ELECTRODOMESTICS = "ELECTRODOMESTICS"
    ELECTRONICA = "ELECTRONICA"
    EQIPAMENT_LAB = "EQIPAMENT_LAB"
    ESPORTS = "ESPORTS"
    FERRAMENTES = "FERRAMENTES"
    INFANTIL = "INFANTIL"
    INSTRUMENTS = "INFANTIL"
    JARDINERIA = "JARDINERIA"
    JOCS_DE_TAULA = "JOCS_DE_TAULA"
    JOIES_COMPLEMENTS_ACCESSORIS = "JOIES_COMPLEMENTS_ACCESSORIS"
    LLIBRES = "LLIBRES"
    MASCOTES = "MASCOTES"
    MOBLES = "MOBLES"
    NETEJA = "NETEJA"
    ROBA = "ROBA"
    SABATES = "SABATES"
    VEHICLES = "VEHICLES"
    VIDEOJOCS = "VIDEOJOCS"


class VerifiedProduct(BaseModel):
    uuid: UUID
    sku: str
    name: str
    description: str
    cahtegory: Cathegory
    stock: int
    price: float
    image: str


class SecondHandProduct(BaseModel):
    uuid: UUID
    name: str
    description: str
    cahtegory: Cathegory
    price: float
    image: str
