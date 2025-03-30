from uuid import UUID

from fastapi import APIRouter, HTTPException

from database import get_db_connection
from model.product import Product

router = APIRouter()


@router.get(
    "/product/{product_id}",
    description="Get detailed information of a specific product",
)
async def get_product(product_id: UUID):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                product = Product()
                product.fetch(cursor, product_id)
                return product

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
