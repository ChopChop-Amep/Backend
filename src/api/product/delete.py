from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg import sql

from auth import authenticate
from database import get_db_connection
from model.user import User

router = APIRouter()

# TODO: OOPize this

@router.delete("/product/{product_id}", description="Delete a product")
async def delete_product(product_id: UUID, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL(
                        "DELETE FROM chopchop.verified_product WHERE vp_id = %s AND vp_owner = %s RETURNING id"
                    ),
                    (product_id, user.id_),
                )
                deleted_id = cursor.fetchone()

                # If it's not a VerifiedProduct, it's probably a SecondHandProduct. Attempt to delete from that table
                if not deleted_id:
                    cursor.execute(
                        sql.SQL(
                            "DELETE FROM chopchop.secondhand_product WHERE sp_id = %s AND sp_owner = %s RETURNING id"
                        ),
                        (product_id, user.id),
                    )
                    deleted_id = cursor.fetchone()

                # If it wasn't a SecondHandProduct either, it's either not an existing product or the user doesn't have permission to delete it. Return an error.
                if not deleted_id:
                    raise HTTPException(status_code=404, detail="Product not found")

        return Response(status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
