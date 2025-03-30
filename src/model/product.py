from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from psycopg import Cursor, sql

from model import User, Particular, Professional, Enterprise


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


# Optional fields only populated when _type == VERIFIED
class Product(BaseModel):
    id_: UUID = Field(..., alias="id")
    owner: UUID
    name: str
    description: str
    price: float
    image: str
    category: Category


class SecondhandProduct(Product):
    def insert(self, cursor: Cursor, user: User):
        if not (isinstance(user, Particular) or isinstance(user, Professional)):
            raise Exception("This user is not allowed to post verified products")

        insert_product_query = sql.SQL("""
            INSERT INTO chopchop.product_id DEFAULT VALUES
            RETURNING product_id
        """)
        cursor.execute(insert_product_query)
        product_id = cursor.fetchone()[0]

        insert_secondhand_query = sql.SQL("""
            INSERT INTO chopchop.secondhand_product (
                sp_id, 
                sp_owner, 
                sp_name, 
                sp_description, 
                sp_price, 
                sp_image, 
                sp_category
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """)
        cursor.execute(
            insert_secondhand_query,
            (
                product_id,
                user.id_,
                self.name,
                self.description,
                self.price,
                self.image,
                self.category.value,
            ),
        )

        return product_id


class VerifiedProduct(Product):
    sku: str
    stock: int
    sold: int

    def insert(self, cursor: Cursor, user: User):
        if not (isinstance(user, Professional) or isinstance(user, Enterprise)):
            raise Exception("This user is not allowed to post verified products")

        insert_product_query = sql.SQL("""
            INSERT INTO chopchop.product_id DEFAULT VALUES
            RETURNING product_id
        """)
        cursor.execute(insert_product_query)
        product_id = cursor.fetchone()[0]

        insert_verified_query = sql.SQL("""
            INSERT INTO chopchop.verified_product (
                vp_id, 
                vp_owner, 
                vp_sku, 
                vp_name, 
                vp_description, 
                vp_stock, 
                vp_price, 
                vp_image, 
                vp_category
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

        cursor.execute(
            insert_verified_query,
            (
                product_id,
                user.id_,
                self.sku,
                self.name,
                self.description,
                self.stock,
                self.price,
                self.image,
                self.category.value,
            ),
        )

        return product_id


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
    category: Category

    def into_product(self):
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
                    sold=0,
                )

            case self.Type.SECONDHAND:
                return SecondhandProduct(
                    name=self.name,
                    description=self.description,
                    price=self.price,
                    image=self.image,
                    category=self.category,
                )
