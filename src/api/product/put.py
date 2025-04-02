from fastapi import APIRouter, Depends, HTTPException

from auth import authenticate
from database import get_db_connection
from model.user import User
from model.product.product import NewProduct

router = APIRouter()


@router.put(
    "/product",
    description="Create a new product",
)
async def post_product(product: NewProduct, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:

                try:
                    product = product.into_product()
                    product_id = product.update(cursor, user)
                    return product_id

                except Exception as e:
                    raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
