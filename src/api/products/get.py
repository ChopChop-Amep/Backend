
from fastapi import APIRouter, HTTPException

from database import get_db_connection
from model.product.product import Product

router = APIRouter()


@router.get(
    "/products",
    description="Get basic information of all products",
)
async def get_products():
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                return Product.get_products(cursor)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
