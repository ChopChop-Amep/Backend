from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from psycopg import Cursor, sql
from fastapi import HTTPException

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

    def fetch(self, cursor: Cursor, product_id: UUID):
        query = """
            SELECT 
                CASE 
                    WHEN vp.vp_id IS NOT NULL THEN 'verified_product'
                    WHEN sp.sp_id IS NOT NULL THEN 'secondhand_product'
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

        match cursor.fetchone():
            case "verified_product":
                return VerifiedProduct.fetch(cursor, product_id)
            case "secondhand_product":
                return SecondhandProduct.fetch(cursor, product_id)
            case None:
                raise HTTPException(status_code=404, detail=str("Product not found"))


class SecondhandProduct(Product):
    def fetch(self, cursor: Cursor, product_id: UUID):
        query_secondhand = sql.SQL(
            """
            SELECT sp_id, sp_owner, sp_name, sp_description, sp_price, sp_image, sp_category
            FROM chopchop.secondhand_product
            WHERE sp_id = %s;
            """
        )
        cursor.execute(query_secondhand, (product_id,))
        response = cursor.fetchone()

        self.id_ = (UUID(response[0]),)
        self.owner = (UUID(response[1]),)
        self.name = (response[2],)
        self.description = (response[3],)
        self.price = (float(response[4]),)
        self.image = (response[5],)
        self.category = (Category(response[6]),)

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

    def fetch(self, cursor: Cursor, product_id: UUID):
        query_verified = sql.SQL(
            """
            SELECT vp_id, vp_owner, vp_sku, vp_name, vp_description, vp_stock, vp_price, vp_image, vp_category, vp_sold
            FROM chopchop.verified_product
            WHERE vp_id = %s;
            """
        )
        cursor.execute(query_verified, (product_id,))
        response = cursor.fetchone()

        self.id_ = (UUID(response[0]),)
        self.owner = (UUID(response[1]),)
        self.sku = (response[2],)
        self.name = (response[3],)
        self.description = (response[4],)
        self.stock = (int(response[5]),)
        self.price = (float(response[6]),)
        self.image = (response[7],)
        self.category = (Category(response[8]),)
        self.sold = (response[9],)

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
