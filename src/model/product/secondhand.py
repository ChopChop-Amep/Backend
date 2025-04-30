from uuid import UUID

from psycopg import Cursor, sql
from fastapi import HTTPException

from model.user import User, Particular, Professional, Admin
from model.product.product import Product


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

        self.id = UUID(response[0])
        self.owner = UUID(response[1])
        self.name = response[2]
        self.description = response[3]
        self.price = float(response[4])
        self.image = response[5]
        self.category = self.Category(response[6])

    def insert(self, cursor: Cursor, user: User):
        if not (isinstance(user, Particular) or isinstance(user, Professional)):
            raise Exception(
                "This user is not allowed to post verified products")

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
                user.id,
                self.name,
                self.description,
                self.price,
                self.image,
                self.category.value,
            ),
        )

        return product_id

    def delete(self, cursor: Cursor, user: User):
        query = "DELETE FROM chopchop.secondhand_product WHERE sp_id = %s AND sp_owner = %s RETURNING 'success'"
        if isinstance(user, Admin):
            query = (  # If tne user is an admin, skip product owner check
                "DELETE FROM chopchop.secondhand_product WHERE sp_id = %s RETURNING 'success'"
            )

        cursor.execute(
            sql.SQL(query),
            (self.id, user.id),
        )
        response = cursor.fetchone()

        if response != "success":
            raise HTTPException(status_code=404, detail="Product not found")

    def update(self, cursor: Cursor, user: User):
        update_secondhand_query = sql.SQL("""
            UPDATE chopchop.secondhand_product
            SET  
                sp_name = %s, 
                sp_description = %s, 
                sp_price = %s, 
                sp_image = %s, 
                sp_category = %s
            WHERE sp_id = %s AND sp_owner = %s
            RETURNING 'success'
        """)
        cursor.execute(
            update_secondhand_query,
            (
                self.name,
                self.description,
                self.price,
                self.image,
                self.category.value,
                self.sp_id,
                user.id,
            ),
        )
        response = cursor.fetchone()

        if response != "success":
            raise HTTPException(status_code=404, detail="Product not found")
