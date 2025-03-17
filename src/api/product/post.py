from fastapi import APIRouter, Depends, HTTPException
from psycopg import sql

from model import VerifiedProduct, SecondHandProduct
from auth import get_current_user, TokenData
from database import get_db_connection

router = APIRouter()


@router.post(
    "/product/verified", description="Post a new verified product to the database"
)
async def post_verified_product(
    product: VerifiedProduct, current_user: TokenData = Depends(get_current_user)
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL(
                        "TODO!"
                    ),
                    (product.name, product.description, product.price),
                )
                product_id = cursor.fetchone()[0]
        return {"message": "Product created", "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.post(
    "/product/secondhand", description="Post a new second hand product to the database"
)
async def post_secondhand_product(product: SecondHandProduct):
    return {"message": "Product created", "product": product}
