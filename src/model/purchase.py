from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from psycopg import sql, Cursor

from model.user import User, Particular, Professional


class Purchase(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    date: Optional[datetime] = None

    # Associative class between purchase and product_id
    class PurchaseItem(BaseModel):
        product_id: UUID
        count: int
        paid: float

    items: List[PurchaseItem] = []

    def __init__(self, user: User, **data):
        # Check if the user is allowed to make purchases
        if not (isinstance(user, Particular) or isinstance(user, Professional)):
            raise Exception("This user is not allowed to make purchases")

        # Call the parent class's __init__ method with the provided data
        super().__init__(user_id=user.id, **data)

    def fetch(self, cursor: Cursor, purchase_id: UUID):
        query_purchase = sql.SQL(
            """
            SELECT pu_date
            FROM chopchop.purchase
            WHERE pu_id = %s AND pu_user_id = %s;
            """
        )
        cursor.execute(query_purchase, (purchase_id, self.user_id))

        response = cursor.fetchone()

        self.id = purchase_id
        self.date = datetime.datetime.fromisoformat(response[1])

        query_purchased_items = sql.SQL(
            """
            SELECT pi_product_id, pi_count, pi_paid
            FROM chopchop.purchase_item
            WHERE pi_purchase_id = %s;
            """
        )
        cursor.execute(query_purchased_items, (purchase_id,))

        response = cursor.fetchall()

        for item in response:
            product_id = item[0]
            count = int(item[1])
            paid = float(item[2])

            item = self.PurchaseItem(product_id, count, paid)

            self.items.append(item)

        return self

    def insert(self, cursor: Cursor, purchased_items: List[PurchaseItem]):
        insert_product_query = sql.SQL("""
            INSERT INTO chopchop.purchase (pu_user_id)
            VALUES (%s)
            RETURNING pu_id
        """)
        cursor.execute(insert_product_query, (self.user_id,))
        purchase_id = cursor.fetchone()[0]

        insert_purchase = sql.SQL("""
            INSERT INTO chopchop.purchase_item (
                pi_purchase_id,
                pi_product_id,
                pi_count,
                pi_paid
            )
            VALUES (%s, %s, %s, %s)
        """)

        for item in purchased_items:
            cursor.execute(
                insert_purchase,
                (
                    purchase_id,
                    item.product_id,
                    item.count,
                    item.paid,
                ),
            )

        return purchase_id

    # No delete or update methods, purchases are final!
