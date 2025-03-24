import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from psycopg import sql

from database import get_db_connection
from model.product import JsonProduct, ProductType

router = APIRouter()


@router.get(
    "/product/{product_id}",
    description="Get detailed information of a specific product",
)
async def get_product(product_id: uuid):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                query_verified = sql.SQL(
                    """
                    SELECT vp_id, vp_owner, vp_sku, vp_name, vp_description, vp_stock, vp_price, vp_image, vp_category, vp_sold
                    FROM VerifiedProduct
                    WHERE vp_id = %s;
                    """
                )
                cursor.execute(query_verified, (product_id,))
                result = cursor.fetchone()

                if result:
                    product = JsonProduct(
                        _type=ProductType.VERIFIED,
                        _id=result[0],
                        owner=result[1],
                        sku=result[2],
                        name=result[3],
                        description=result[4],
                        stock=result[5],
                        price=result[6],
                        image=result[7],
                        category=result[8],
                        sold=result[9],
                    )
                    return product

                # If it's not a VerifiedProduct, it probably is a SecondHandProduct
                query_second_hand = sql.SQL(
                    """
                    SELECT sp_id, sp_owner, sp_name, sp_description, sp_price, sp_image, sp_category
                    FROM SecondHandProduct
                    WHERE sp_id = %s;
                    """
                )
                cursor.execute(query_second_hand, (product_id,))
                result = cursor.fetchone()

                if result:
                    product = JsonProduct(
                        _type=ProductType.VERIFIED,
                        _id=result[0],
                        owner=result[1],
                        sku=None,
                        name=result[2],
                        description=result[3],
                        stock=None,
                        price=result[4],
                        image=result[5],
                        category=result[6],
                        sold=None,
                    )
                    return product

                # If it's not in either, then it doesn't exist
                raise HTTPException(
                    status_code=404, detail="Product not found")

        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
