from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from psycopg import Cursor
from fastapi import HTTPException


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
                from model.product.verified import VerifiedProduct

                product = VerifiedProduct(_id=product_id)
                return product

            case "secondhand":
                from model.product.secondhand import SecondhandProduct

                return SecondhandProduct(_id=product_id)

            case "not found":
                raise HTTPException(
                    status_code=404, detail="Product not found")

            case _:
                raise HTTPException(
                    status_code=500,
                    detail="Something unexpected happened at model/product.py:Product.into_child:78",
                )

    @staticmethod
    def get_products(cursor: Cursor):
        print("CRIDAT GET_PRODUCTS CLASE PRODUCT")
        query = """
                SELECT 
                        vp_id, vp_name, vp_image 
                        FROM chopchop.verified_product

                    UNION

                SELECT 
                        sp_id, sp_name, sp_image
                        FROM chopchop.secondhand_product;

                """
        cursor.execute(query)
        result = cursor.fetchall()
        print(result)
        return result


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

                from model.product.verified import VerifiedProduct

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
                from model.product.secondhand import SecondhandProduct

                return SecondhandProduct(
                    name=self.name,
                    description=self.description,
                    price=self.price,
                    image=self.image,
                    category=self.category,
                )
