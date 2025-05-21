from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from psycopg import sql, Cursor
from fastapi import HTTPException


class Rating(BaseModel):
    owner_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    rating: Optional[float] = None

    def fetch(self, cursor: Cursor):
        """Fetch a rating by owner and product ID"""
        query = sql.SQL("""
            SELECT ra_owner_id, ra_product_id, ra_rating
            FROM chopchop.ratings
            WHERE ra_owner_id = %s AND ra_product_id = %s;
        """)
        cursor.execute(query, (self.owner_id, self.product_id))
        response = cursor.fetchone()

        if not response:
            raise HTTPException(status_code=404, detail="Rating not found")

        self.owner_id = response[0]
        self.product_id = response[1]
        self.rating = float(response[2])
        return self

    def insert(self, cursor: Cursor):
        """Insert a new rating"""
        insert_query = sql.SQL("""
            INSERT INTO chopchop.ratings (
                ra_owner_id,
                ra_product_id,
                ra_rating
            )
            VALUES (%s, %s, %s)
            RETURNING ra_owner_id, ra_product_id;
        """)

        cursor.execute(
            insert_query,
            (
                self.owner_id,
                self.product_id,
                self.rating,
            ),
        )

        return cursor.fetchone()

    def update(self, cursor: Cursor):
        """Update an existing rating"""
        update_query = sql.SQL("""
            UPDATE chopchop.ratings
            SET ra_rating = %s
            WHERE ra_owner_id = %s AND ra_product_id = %s
            RETURNING ra_owner_id, ra_product_id;
        """)

        cursor.execute(
            update_query,
            (
                self.rating,
                self.owner_id,
                self.product_id,
            ),
        )

        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Rating not found")

        return result

    @staticmethod
    def get_product_rating(cursor: Cursor, product_id: UUID):
        # Try to get from secondhand_product
        query_secondhand = sql.SQL("""
            SELECT rating
            FROM chopchop.secondhand_product
            WHERE sp_id = %s;
        """)
        cursor.execute(query_secondhand, (product_id,))
        result = cursor.fetchone()

        if result and result[0] is not None:
            return {
                "product_id": product_id,
                "rating": float(result[0])
            }

        # Try to get from verified_product
        query_verified = sql.SQL("""
            SELECT rating
            FROM chopchop.verified_product
            WHERE vp_id = %s;
        """)
        cursor.execute(query_verified, (product_id,))
        result = cursor.fetchone()

        if result and result[0] is not None:
            return {
                "product_id": product_id,
                "rating": float(result[0])
            }

        raise HTTPException(
            status_code=404, detail="Product not found or has no rating")
