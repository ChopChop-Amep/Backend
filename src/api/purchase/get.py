from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from auth import authenticate
from database import get_db_connection
from model.purchase import Purchase
from model.user import User

from datetime import date as Date
from typing import Optional

router = APIRouter()


@router.get(
    "/purchase/{purchase_id}",
    description="Retrieve a purchase by ID",
)
async def get_products(purchase_id: UUID, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Purchase(user).fetch(cursor, purchase_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


@router.get(
    "/purchase/my_purchases",
    description="Retrieve all purchases ordered by date of the user"
)
async def get_my_purchases(date: Optional[Date] = None, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Purchase(user).my_purchases(cursor, date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
