from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from psycopg import Cursor
from fastapi import HTTPException

from model.product.secondhand import SecondhandProduct
from model.product.verified import VerifiedProduct


class Product(BaseModel):
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

    id_: Optional[UUID] = Field(default=None, alias="id")
    owner: Optional[UUID] = None
    name: str = ""
    description: str = ""
    price: float = 0.0
    image: str = ""
    category: Category = Category.ALTRES

    @staticmethod
    def factory(cursor: Cursor, product_id: UUID):
        query = """
            SELECT 
                CASE 
                    WHEN vp.vp_id IS NOT NULL THEN 'verified'
                    WHEN sp.sp_id IS NOT NULL THEN 'secondhand'
                    ELSE 'not found'
                    END AS product_type
                FROM 
                    chopchop.product_id p
                LEFT JOIN 
                    chopchop.verified_product vp ON p.product_id = vp.vp_id
                LEFT JOIN 
                    chopchop.secondhand_product sp ON p.product_id = sp.sp_id
                WHERE 
                    p.product_id = %s;
        """
        cursor.execute(query, (product_id,))

        match cursor.fetchone()[0]:
            case "verified":
                product = VerifiedProduct(_id=product_id)
                return product

            case "secondhand":
                return SecondhandProduct(_id=product_id)

            case "not found":
                raise HTTPException(status_code=404, detail="Product not found")

            case _:
                raise HTTPException(
                    status_code=500,
                    detail="Something unexpected happened at model/product.py:Product.into_child:78",
                )


# Used to seralize the recieved json for the POST request on /product
class NewProduct(BaseModel):
    class Type(Enum):
        VERIFIED = "verified"
        SECONDHAND = "secondhand"

    type_: Type = Field(..., alias="type")
    sku: Optional[str]
    name: str
    description: str
    stock: Optional[int]
    price: float
    image: str
    category: Product.Category

    def factory(self):
        match self.type_:
            case self.Type.VERIFIED:
                if self.sku is None or self.stock is None:
                    raise Exception(
                        "SKU and stock must be provided for verified products."
                    )

                return VerifiedProduct(
                    sku=self.sku,
                    name=self.name,
                    description=self.description,
                    stock=self.stock,
                    price=self.price,
                    image=self.image,
                    category=self.category,
                )

            case self.Type.SECONDHAND:
                return SecondhandProduct(
                    name=self.name,
                    description=self.description,
                    price=self.price,
                    image=self.image,
                    category=self.category,
                )
