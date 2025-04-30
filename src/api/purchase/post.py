from typing import List

from fastapi import APIRouter, Depends, HTTPException

from auth import authenticate
from database import get_db_connection
from model.purchase import Purchase
from model.user import User

router = APIRouter()


@router.post(
    "/purchase",
    description="Make a purchase",
)
async def post_product(
    items: List[Purchase.PurchaseItem], user: User = Depends(authenticate)
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = (
                    False  # We have to insert several tables, so use a transaction
                )

                try:
                    purchase_id = Purchase(user).insert(cursor, items)
                    conn.commit()  # Commit the transaction if all is well

                    return purchase_id

                except Exception as e:
                    conn.rollback()
                    raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
