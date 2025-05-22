from fastapi import APIRouter, Depends, HTTPException

from database import get_db_connection
from model.rating import Rating
from model.user import User
from auth import authenticate


router = APIRouter()


@router.post("/rating", description="Submit or update a rating")
async def post_rating(rating: Rating, user: User = Depends(authenticate)):
    rating.owner_id = user.id  # Inject authenticated user ID

    if not rating.product_id:
        raise HTTPException(status_code=400, detail="Missing product_id")

    if rating.value is None or not (1.0 <= rating.value <= 5.0):
        raise HTTPException(
            status_code=400, detail="Rating must be between 1 and 5")

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = False

                # Check if the user has purchased this product
                cursor.execute(
                    """
                    SELECT 1
                    FROM chopchop.purchase_item pi
                    JOIN chopchop.purchase p ON pi.pi_purchase_id = p.pu_id
                    WHERE pi.pi_product_id = %s AND p.pu_user_id = %s
                    LIMIT 1;
                """,
                    (str(rating.product_id), str(rating.owner_id)),
                )

                if not cursor.fetchone():
                    raise HTTPException(
                        status_code=403, detail="User has not purchased this product"
                    )

                try:
                    # Check if rating already exists
                    cursor.execute(
                        """
                        SELECT 1 FROM chopchop.ratings
                        WHERE ra_product_id = %s AND ra_owner_id = %s
                    """,
                        (str(rating.product_id), str(rating.owner_id)),
                    )

                    if cursor.fetchone():
                        rating.update(cursor)
                    else:
                        rating.insert(cursor)

                    conn.commit()
                    return {"message": "Rating submitted successfully"}

                except Exception as e:
                    conn.rollback()
                    raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
