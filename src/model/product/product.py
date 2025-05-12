from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from psycopg import Cursor
from fastapi import HTTPException

PRODUCTS_PER_PAGE = 12


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

    id: Optional[UUID] = None
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
    def get_products(
        cursor: Cursor,
        query: Optional[str],
        page: int,
        category: Optional[Category],
        price_min: float,
        price_max: float,
        owner: Optional[UUID],
    ):
        sql_query = """
            WITH products AS (
                SELECT vp_id AS id, vp_name AS name, vp_image AS image, vp_price AS price, vp_category AS category, vp_owner AS owner
                FROM chopchop.verified_product

                UNION

                SELECT sp_id AS id, sp_name AS name, sp_image AS image, sp_price as PRICE, sp_category AS category, sp_owner AS owner
                FROM chopchop.secondhand_product
            )
            SELECT id, name, image, price FROM products
        """
        sql_query_parameters = []
        conditions = []

        # ============== Add filters =============== #
        if query:
            conditions.append("name ILIKE %s%")
            sql_query_parameters.append(f"%{query}%")

        if category:
            conditions.append("category = %s")
            sql_query_parameters.append(category)

        if owner:
            conditions.append("owner = %s")
            sql_query_parameters.append(owner)

        conditions.append("""
            price BETWEEN %s AND %s
            LIMIT %s OFFSET %s
        """)
        sql_query_parameters.extend(
            [price_min, price_max, PRODUCTS_PER_PAGE, page * PRODUCTS_PER_PAGE]
        )

        sql_query += " WHERE " + " AND ".join(conditions)
        # ========================================== #

        cursor.execute(sql_query, sql_query_parameters)
        results = cursor.fetchall()

        def to_dict(result):
            return {
                "id": result[0],
                "name": result[1],
                "image": result[2],
                "price": result[3]
            }

        products = list(map(to_dict, results))
        return products


# Used to seralize the recieved json for the POST request on /product
class NewProduct(BaseModel):
    class Type(Enum):
        VERIFIED = "verified"
        SECONDHAND = "secondhand"

    type: Type
    sku: Optional[str]
    name: str
    description: str
    stock: Optional[int]
    price: float
    image: str
    category: Product.Category

    def factory(self):
        match self.type:
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
