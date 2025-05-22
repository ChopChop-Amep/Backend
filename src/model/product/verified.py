from uuid import UUID

from psycopg import Cursor, sql
from fastapi import HTTPException

from model.user import User, Professional, Enterprise, Admin
from model.product.product import Product


class VerifiedProduct(Product):
    sku: str = ""
    stock: int = 0
    sold: int = 0

    def fetch(self, cursor: Cursor, product_id: UUID):
        query_verified = sql.SQL(
            """
            SELECT vp_id, vp_owner, vp_sku, vp_name, vp_description, vp_stock, vp_price, vp_image, vp_category, vp_sold, vp_rating ,vp_discount, vp_deleted, vp_condition
            FROM chopchop.verified_product
            WHERE vp_id = %s;
            """
        )
        cursor.execute(query_verified, (product_id,))

        response = cursor.fetchone()

        self.id = response[0]
        self.owner = response[1]
        self.sku = response[2]
        self.name = response[3]
        self.description = response[4]
        self.stock = int(response[5])
        self.price = float(response[6])
        self.image = response[7]
        self.category = self.Category(response[8])
        self.sold = response[9]
        self.rating = response[10]
        self.discount = response[11]
        self.deleted = response[12]
        self.condition = "nou"

    def insert(self, cursor: Cursor, user: User):
        if not (isinstance(user, Professional) or isinstance(user, Enterprise)):
            raise Exception(
                "This user is not allowed to post verified products")

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
                vp_category,
                vp_condition
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

        cursor.execute(
            insert_verified_query,
            (
                product_id,
                user.id,
                self.sku,
                self.name,
                self.description,
                self.stock,
                self.price,
                self.image,
                self.category.value,
                self.condition.value
            ),
        )

        return product_id

    def delete(self, cursor: Cursor, user: User):
        query = "DELETE FROM chopchop.verified_product WHERE vp_id = %s AND vp_owner = %s RETURNING 'success'"
        if isinstance(user, Admin):
            query = (  # If tne user is an admin, skip product owner check
                "DELETE FROM chopchop.verified_product WHERE vp_id = %s RETURNING 'success'"
            )

        cursor.execute(
            sql.SQL(query),
            (self.id, user.id),
        )
        response = cursor.fetchone()

        if response != "success":
            raise HTTPException(status_code=404, detail="Product not found")

    def update(self, cursor: Cursor, user: User):
        update_verified_query = sql.SQL("""
            UPDATE chopchop.verified_product
            SET 
                vp_name = %s, 
                vp_description = %s, 
                vp_stock = %s, 
                vp_price = %s, 
                vp_image = %s, 
                vp_category = %s
            WHERE vp_id = %s AND vp_owner = %s
            RETURNING 'success'
        """)

        cursor.execute(
            update_verified_query,
            (
                self.name,
                self.description,
                self.stock,
                self.price,
                self.image,
                self.category.value,
                self.vp_id,
                user.id,
            ),
        )
        response = cursor.fetchone()

        if response != "success":
            raise Exception(
                "This user is not allowed to post verified products")
            raise HTTPException(status_code=404, detail="Product not found")
