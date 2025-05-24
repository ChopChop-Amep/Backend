from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from auth import authenticate
from database import get_db_connection
from model.product.product import Product
from model.user import User

router = APIRouter()


@router.get(
    "/products",
    description="Get basic information of all products",
)
async def get_products(
    query: Optional[str] = Query(None),
    page: Optional[int] = Query(0),
    category: Optional[Product.Category] = Query(None),
    condition: Optional[Product.Condition] = Query(None),
    rating: Optional[int] = Query(None, ge=1, le=5),
    min_price: Optional[float] = Query(0.0),
    max_price: Optional[float] = Query(float("inf")),
    owner: Optional[UUID] = Query(None),
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Product.get_products(
                    cursor,
                    query,
                    page,
                    category,
                    condition,
                    rating,
                    min_price,
                    max_price,
                    owner,
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get(
    "/my/products",
    description="Get basic information of all the user's products",
)
async def get_my_products(
    user: User = Depends(authenticate),
    page: Optional[int] = Query(0),
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Product.get_products(
                    cursor,
                    page,
                    user.id,
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
