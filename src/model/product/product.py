from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from psycopg import Cursor
from fastapi import HTTPException

PRODUCTS_PER_PAGE = 12


class Product(BaseModel):
    class Category(Enum):
        artesanal = "artesanal"
        antiguitats = "antiguitats"
        cosmetica = "cosmetica"
        cuina = "cuina"
        electrodomestics = "electrodomestics"
        electronica = "electronica"
        equipament_lab = "equipament_lab"
        esports = "esports"
        ferramentes = "ferramentes"
        infantil = "infantil"
        instruments = "instruments"
        jardineria = "jardineria"
        jocs_de_taula = "jocs_de_taula"
        joies_complements_accessoris = "joies_complements_accessoris"
        llibres = "llibres"
        mascotes = "mascotes"
        mobles = "mobles"
        neteja = "neteja"
        roba = "roba"
        sabates = "sabates"
        vehicles = "vehicles"
        videojocs = "videojocs"

        altres = "altres"

    class Condition(Enum):
        nou = "nou"
        com_nou = "com_nou"
        usat = "usat"
        amb_defectes = "amb_defectes"
        per_recanvis = "per_recanvis"
        none = "-"

    id: Optional[UUID] = None
    owner: Optional[UUID] = None
    name: str = ""
    description: str = ""
    price: float = 0.0
    image: str = ""
    rating: float = 0.0
    discount: float = 0.0
    deleted: bool = False
    category: Category = Category.altres
    condition: Condition = Condition.none

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
        category: Optional["Product.Category"],
        condition: Optional["Product.Condition"],
        rating: Optional[int],
        min_price: float,
        max_price: float,
        owner: Optional[UUID] = None,
    ):
        sql_query = """
            WITH products AS (
                SELECT 
                    vp_id AS id, 
                    vp_name AS name, 
                    vp_image AS image, 
                    vp_price AS price, 
                    vp_category AS category, 
                    vp_owner AS owner, 
                    vp_rating AS rating, 
                    vp_discount AS discount, 
                    vp_deleted AS deleted, 
                    vp_condition AS condition
                FROM chopchop.verified_product
                WHERE vp_deleted = FALSE

                UNION

                SELECT 
                    sp_id AS id, 
                    sp_name AS name, 
                    sp_image AS image, 
                    sp_price as price, 
                    sp_category AS category, 
                    sp_owner AS owner, 
                    sp_rating AS rating, 
                    sp_discount AS discount, 
                    sp_deleted AS deleted, 
                    sp_condition AS condition
                FROM chopchop.secondhand_product
                WHERE sp_deleted = FALSE
            )
            SELECT id, name, image, price, category, rating, discount, condition FROM products
        """

        sql_query_parameters = []
        conditions = []

        # ===== Add filters =====
        if query:
            conditions.append("name ILIKE %s")
            sql_query_parameters.append(f"%{query}%")

        if category:
            conditions.append("category = %s")
            sql_query_parameters.append(category)

        if condition:
            conditions.append("condition = %s")
            sql_query_parameters.append(condition)

        if rating:
            conditions.append("rating >= %s AND rating < %s")
            sql_query_parameters.extend([float(rating), 5.0])

        if owner:
            conditions.append("owner = %s")
            sql_query_parameters.append(owner)

        conditions.append("price BETWEEN %s AND %s")
        sql_query_parameters.extend([min_price, max_price])

        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)
        # =======================

        if rating:
            sql_query += " ORDER BY rating DESC"

        sql_query += " LIMIT %s OFFSET %s"
        sql_query_parameters.extend(
            [PRODUCTS_PER_PAGE, page * PRODUCTS_PER_PAGE])

        cursor.execute(sql_query, sql_query_parameters)
        results = cursor.fetchall()

        def to_dict(result):
            return {
                "id": result[0],
                "name": result[1],
                "image": result[2],
                "price": result[3],
                "category": result[4],
                "rating": result[5],
                "discount": result[6],
                "condition": result[7],
            }

        return list(map(to_dict, results))


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
    condition: Product.Condition

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
                    condition=self.condition,
                )

            case self.Type.SECONDHAND:
                from model.product.secondhand import SecondhandProduct

                return SecondhandProduct(
                    name=self.name,
                    description=self.description,
                    price=self.price,
                    image=self.image,
                    category=self.category,
                    condition=self.condition,
                )
