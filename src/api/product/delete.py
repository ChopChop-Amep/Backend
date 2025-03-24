from fastapi import APIRouter, Depends, HTTPException
from psycopg import sql
from uuid import UUID

from auth import get_current_user, TokenData
from database import get_db_connection

router = APIRouter()


@router.delete(
    "/product/delete", description="Delete a product from the database"
)
async def delete_product(
    product_id: UUID, current_user: TokenData = Depends(get_current_user)
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("DELETE FROM products WHERE id = %s RETURNING id"),
                    (product_id,)
                )
                deleted_id = cursor.fetchone()
                if not deleted_id:
                    raise HTTPException(
                        status_code=404, detail="Product not found")
        return {"message": "Product deleted", "product_id": product_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
