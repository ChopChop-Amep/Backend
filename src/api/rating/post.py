from uuid import UUID

from fastapi import APIRouter, HTTPException

from database import get_db_connection
from model.rating import Rating

router = APIRouter()


@router.post("/rating", description="Submit a new rating or update an existing one")
async def post_rating(
    product_id: UUID,
    owner_id: UUID,
    rating_value: float
):
    if rating_value < 1 or rating_value > 5:
        raise HTTPException(
            status_code=400, detail="Rating must be between 1 and 5")

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = False

                # Verificar si l'usuari ha comprat aquest producte
                cursor.execute("""
                    SELECT 1
                    FROM chopchop.purchase_item pi
                    JOIN chopchop.purchase p ON pi.pi_purchase_id = p.pu_id
                    WHERE pi.pi_product_id = %s AND p.pu_user_id = %s
                    LIMIT 1;
                """, (str(product_id), str(owner_id)))

                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=403, detail="User has not purchased this product")

                # Comprovar si ja hi ha un rating per aquest usuari i producte
                cursor.execute("""
                    SELECT 1
                    FROM chopchop.ratings
                    WHERE ra_product_id = %s AND ra_owner_id = %s
                """, (str(product_id), str(owner_id)))
                rating = Rating(product_id=product_id,
                                owner_id=owner_id, rating=rating_value)

                try:
                    if cursor.fetchone():
                        rating.update(cursor)
                    else:
                        rating.insert(cursor)

                    conn.commit()

                except Exception as e:
                    conn.rollback()
                    raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
