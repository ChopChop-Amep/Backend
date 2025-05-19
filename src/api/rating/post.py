from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Body

from database import get_db_connection
from model.rating import Rating

router = APIRouter()


@router.post(
    "/rating",
    description="Submit a new rating or update an existing one",
)
async def post_rating(
    product_id: UUID = Body(...),
    rating_value: float = Body(..., ge=0, le=5)
):
    if rating_value < 1 or rating_value > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = False  # Use a transaction

                try:
                    rating = Rating(product_id, rating_value)
                    rating_id = rating.insert(cursor)
                    conn.commit()  # Commit if everything went well
                    return {"id": rating_id}

                except Exception as e:
                    conn.rollback()  # Rollback on error
                    raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
