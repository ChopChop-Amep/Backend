from typing import Optional

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
    min_price: Optional[float] = Query(0.0),
    max_price: Optional[float] = Query(float("inf")),
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Product.get_products(
                    cursor, query, page, category, min_price, max_price
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
