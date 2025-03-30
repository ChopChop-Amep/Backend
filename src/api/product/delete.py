from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from auth import authenticate
from database import get_db_connection
from model.user import User
from model.product.product import Product

router = APIRouter()


@router.delete("/product/{product_id}", description="Delete a product")
async def delete_product(product_id: UUID, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                product = Product.factory(cursor, product_id)
                product.delete(cursor, user)

                # If it wasn't a SecondHandProduct either, it's either not an existing product or the user doesn't have permission to delete it. Return an error.
                if not product:
                    raise HTTPException(status_code=404, detail="Product not found")

        return Response(status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
