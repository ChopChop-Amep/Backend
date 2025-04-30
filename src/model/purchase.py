from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel
from psycopg import sql, Cursor

from model.user import User, Enterprise


class Purchase(BaseModel):
    id: UUID
    user_id: UUID
    date: datetime

    # Associative class between purchase and product_id
    class PurchaseItem(BaseModel):
        product_id: UUID
        count: int
        paid: float

        def __init__(self, product_id: UUID, count: int, paid: float):
            self.product_id = product_id
            self.count = count
            self.paid = paid

    items: List[PurchaseItem] = []

    @classmethod
    def fetch(self, cursor: Cursor, user: User, purchase_id: UUID):
        query_purchase = sql.SQL(
            """
            SELECT pu_date
            FROM chopchop.purchase
            WHERE pu_id = %s AND pu_user_id = %s;
            """
        )
        cursor.execute(query_purchase, (purchase_id, user.id))

        response = cursor.fetchone()

        self.id = purchase_id
        self.user_id = user.id
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
