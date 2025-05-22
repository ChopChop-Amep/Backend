from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from database import get_db_connection
from model.product.product import Product

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
    owner: Optional[UUID] = Query(None)
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Product.get_products(
                    cursor, query, page, category, condition, rating, min_price, max_price, owner
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get(
    "/popular_products",
    description="Get top popular products sorted by rating"
)
async def get_populars():
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Product.get_populars(cursor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
