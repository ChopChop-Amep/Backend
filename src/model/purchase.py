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

        def __init__(self, product_id: UUID, count: int, paid: float):
            self.product_id = product_id
            self.count = count
            self.paid = paid

    items: List[PurchaseItem] = []

    def __init__(self, user: User):
        if not (isinstance(user, Particular) or isinstance(user, Professional)):
            raise Exception("This user is not allowed to make purchases")

        self.user_id = user.id

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
                pi_paid,
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


def my_purchases(self, cursor: Cursor, filter_date: Optional[datetime.date] = None):
    if filter_date:
        query = sql.SQL("""
            SELECT pu_id, pu_date
            FROM chopchop.purchase
            WHERE pu_user_id = %s
            AND DATE(pu_date) = %s
            ORDER BY pu_date DESC;
        """)
        cursor.execute(query, (self.user_id, filter_date))
    else:
        query = sql.SQL("""
            SELECT pu_id, pu_date
            FROM chopchop.purchase
            WHERE pu_user_id = %s
            ORDER BY pu_date DESC;
        """)
        cursor.execute(query, (self.user_id,))

    purchases = cursor.fetchall()
    results = []

    for purchase_id, pu_date in purchases:
        purchase_data = {
            "id": str(purchase_id),
            "date": pu_date.isoformat(),
            "items": []
        }

        # Get associated purchase items
        cursor.execute(
            sql.SQL("""
                SELECT pi_product_id, pi_count, pi_paid
                FROM chopchop.purchase_item
                WHERE pi_purchase_id = %s;
            """),
            (purchase_id,)
        )
        items = cursor.fetchall()

        for product_id, count, paid in items:
            purchase_data["items"].append({
                "product_id": str(product_id),
                "count": count,
                "paid": float(paid)
            })

        results.append(purchase_data)

    return results

    # No delete or update methods, purchases are final!
