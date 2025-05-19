from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from psycopg import sql, Cursor

from model.user import User


class Rating(BaseModel):
    id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    rating: Optional[float] = None


    def fetch(self, cursor: Cursor, rating_id: UUID):
        """Fetch a rating by ID"""
        query = sql.SQL(
            """
            SELECT ra_id, ra_product_id, ra_rating
            FROM chopchop.ratings
            WHERE ra_id = %s;
            """
        )
        cursor.execute(query, (rating_id,))

        response = cursor.fetchone()
        if not response:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Rating not found")

        self.id = response[0]
        self.product_id = response[1]
        self.rating = float(response[2])

        return self

    def insert(self, cursor: Cursor):
        insert_query = sql.SQL("""
            INSERT INTO chopchop.ratings (
                ra_product_id,
                ra_rating
            )
            VALUES (%s, %s)
            RETURNING ra_id
        """)
        
        cursor.execute(
            insert_query,
            (
                self.product_id,
                self.rating,
            ),
        )
        
        rating_id = cursor.fetchone()[0]
        self.id = rating_id
        
        return rating_id

    def update(self, cursor: Cursor):
        """Update an existing rating"""
        update_query = sql.SQL("""
            UPDATE chopchop.ratings
            SET ra_rating = %s
            WHERE ra_product_id = %s
            RETURNING ra_id
        """)
        
        cursor.execute(
            update_query,
            (
                self.rating,
                self.product_id,
            ),
        )
        
        result = cursor.fetchone()
        if not result:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Rating not found")
            
        rating_id = result[0]
        self.id = rating_id
        
        return rating_id
        
    @staticmethod
    def get_product_rating(cursor: Cursor, product_id: UUID):
        """Get rating for a product"""
        query = sql.SQL(
            """
            SELECT ra_id, ra_product_id, ra_rating
            FROM chopchop.ratings
            WHERE ra_product_id = %s;
            """
        )
        cursor.execute(query, (product_id,))
        
        result = cursor.fetchone()
        if not result:
            return None
            
        return {
            "id": result[0],
            "product_id": result[1],
            "rating": float(result[2])
        }