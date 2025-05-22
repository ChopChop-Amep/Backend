from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from psycopg import sql, Cursor


class Rating(BaseModel):
    owner_id: UUID
    product_id: UUID
    value: float = 0.0

    def fetch(self, cursor: Cursor):
        query = sql.SQL("""
            SELECT ra_rating
            FROM chopchop.ratings
            WHERE ra_owner_id = %s AND ra_product_id = %s;
        """)
        cursor.execute(query, (self.owner_id, self.product_id))
        response = cursor.fetchone()

        if not response:
            raise HTTPException(status_code=404, detail="Rating not found")

        self.value = float(response[0])

    def insert(self, cursor: Cursor):
        insert_query = sql.SQL("""
            INSERT INTO chopchop.ratings (
                ra_owner_id,
                ra_product_id,
                ra_rating
            )
            VALUES (%s, %s, %s)
            RETURNING 'success';
        """)

        cursor.execute(
            insert_query,
            (
                self.owner_id,
                self.product_id,
                self.value,
            ),
        )
        success = cursor.fetchone()

        if not success or success != "success":
            raise HTTPException(
                status_code=409, detail="Rating could not be inserted")

        return self.product_id

    def update(self, cursor: Cursor):
        update_query = sql.SQL("""
            UPDATE chopchop.ratings
            SET ra_rating = %s
            WHERE ra_owner_id = %s AND ra_product_id = %s
            RETURNING 'success'
        """)

        cursor.execute(
            update_query,
            (
                self.value,
                self.owner_id,
                self.product_id,
            ),
        )

        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Rating not found")

        return result
