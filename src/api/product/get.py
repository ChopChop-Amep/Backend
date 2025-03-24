# - LA QUERY ES NOMES PER PRODUCTES VERIFICATS, CAL CANVIARHO

# - DEPEN DE LES CLASES DE PRODUCTES
#  QUE TENEN UN ATRIBUT "cahtegory", OJO SI ES CORREGEIX

from fastapi import APIRouter, HTTPException
from psycopg import sql
import uuid

from database import get_db_connection

router = APIRouter()


@router.get("/product/{product_id}",
            description="Get detailed information of a specific product")
async def get_product(
    product_id: uuid
):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                query = sql.SQL(
                    """
                    SELECT *
                    FROM verified_products
                    WHERE uuid = %s;
                    """
                )
                cursor.execute(query, (product_id,))
                result = cursor.fetchone()
                if not result:
                    raise HTTPException(
                        status_code=404, detail="Product not found")

                if len(result) == 8:
                    product = {
                        "uuid": result[0],
                        "sku": result[1],
                        "name": result[2],
                        "description": result[3],
                        "cahtegory": result[4],
                        "stock": result[5],
                        "price": result[6],
                        "image": result[7]
                    }
                else:
                    product = {
                        "uuid": result[0],
                        "name": result[1],
                        "description": result[2],
                        "cahtegory": result[3],
                        "price": result[4],
                        "image": result[5]
                    }

        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
