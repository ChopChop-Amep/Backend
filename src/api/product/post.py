from fastapi import APIRouter, Depends, HTTPException

from auth import authenticate
from database import get_db_connection
from model.product import NewProduct
from model.user import User

router = APIRouter()


@router.post(
    "/product",
    description="Create a new product",
)
async def post_product(product: NewProduct, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = (
                    False  # Utilitzar una transacció ja que hi ha 2 insercions
                )

                try:
                    product = product.into_product()
                    product_id = product.insert(cursor, user)
                    conn.commit()  # Cometre la transacció si tot ha anat bé
                    return product_id

                except Exception as e:
                    conn.rollback()  # Fer rollback si cap inserció falla
                    raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
