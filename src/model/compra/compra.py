from uuid import UUID
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from psycopg import Cursor, sql
from fastapi import HTTPException

from model.user import User


class Compra(BaseModel):
    id_: Optional[UUID] = Field(default=None, alias="id")
    user_id: UUID
    data: datetime = Field(default_factory=datetime.now)
    products: List[UUID] = []

    @staticmethod
    def get_compra(cursor: Cursor, compra_id: UUID):
        query = """
            SELECT co_id, co_user_id, co_data
            FROM chopchop.compra
            WHERE co_id = %s;
        """
        cursor.execute(query, (compra_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Compra not found")

        compra = Compra(
            id_=result[0],
            user_id=result[1],
            data=result[2]
        )

        # Fetch associated products
        product_query = """
            SELECT cop_product_id
            FROM chopchop.compra_product
            WHERE cop_compra_id = %s;
        """
        cursor.execute(product_query, (compra_id,))
        product_results = cursor.fetchall()

        compra.products = [UUID(product[0]) for product in product_results]

        return compra

    def insert(self, cursor: Cursor, user: User):
        if str(user.id_) != str(self.user_id):
            raise HTTPException(
                status_code=403, detail="User can only create purchases for themselves")

        insert_compra_query = sql.SQL("""
            INSERT INTO chopchop.compra (co_user_id, co_data)
            VALUES (%s, %s)
            RETURNING co_id
        """)
        cursor.execute(insert_compra_query, (self.user_id, self.data))
        compra_id = cursor.fetchone()[0]

        # Insert associated products
        for product_id in self.products:
            insert_product_query = sql.SQL("""
                INSERT INTO chopchop.compra_product (cop_compra_id, cop_product_id)
                VALUES (%s, %s)
            """)
            cursor.execute(insert_product_query, (compra_id, product_id))

            # Update stock for verified products
            update_stock_query = sql.SQL("""
                UPDATE chopchop.verified_product
                SET vp_stock = vp_stock - 1, vp_sold = vp_sold + 1
                WHERE vp_id = %s AND vp_stock > 0
            """)
            cursor.execute(update_stock_query, (product_id,))

        self.id_ = compra_id
        return compra_id

    def extreure_factura(self, cursor: Cursor):
        if not self.id_:
            raise HTTPException(
                status_code=400, detail="Cannot generate invoice for unsaved purchase")

        # Get user information
        user_query = """
            SELECT name, surname, nif
            FROM (
                SELECT u_name as name, u_surname as surname, p_nif as nif
                FROM chopchop.particular
                JOIN chopchop.user ON p_id = u_id
                WHERE p_id = %s
                
                UNION
                
                SELECT u_name as name, u_surname as surname, pr_nif as nif
                FROM chopchop.professional
                JOIN chopchop.user ON pr_id = u_id
                WHERE pr_id = %s
                
                UNION
                
                SELECT u_name as name, u_surname as surname, e_nif as nif
                FROM chopchop.enterprise
                JOIN chopchop.user ON e_id = u_id
                WHERE e_id = %s
            ) AS user_info
        """
        cursor.execute(user_query, (self.user_id, self.user_id, self.user_id))
        user_info = cursor.fetchone()

        # Get product information
        products_query = """
            WITH products AS (
                SELECT vp_id AS id, vp_name AS name, vp_price AS price, vp_sku AS sku, 'verified' AS type
                FROM chopchop.verified_product
                WHERE vp_id = ANY(%s)
                
                UNION
                
                SELECT sp_id AS id, sp_name AS name, sp_price AS price, NULL AS sku, 'secondhand' AS type
                FROM chopchop.secondhand_product
                WHERE sp_id = ANY(%s)
            )
            SELECT id, name, price, sku, type FROM products
        """
        cursor.execute(products_query, (self.products, self.products))
        products_info = cursor.fetchall()

        # Generate invoice data
        invoice = {
            "invoice_id": str(self.id_),
            "date": self.data.strftime("%Y-%m-%d %H:%M:%S"),
            "customer": {
                "name": user_info[0],
                "surname": user_info[1],
                "nif": user_info[2] if user_info[2] else "N/A"
            },
            "products": [
                {
                    "id": str(product[0]),
                    "name": product[1],
                    "price": float(product[2]),
                    "sku": product[3] if product[3] else "N/A",
                    "type": product[4]
                }
                for product in products_info
            ],
            "total": sum(float(product[2]) for product in products_info)
        }

        return invoice
