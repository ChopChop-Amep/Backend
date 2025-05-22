from uuid import UUID

from fastapi import APIRouter, HTTPException

from database import get_db_connection
from model.rating import Rating

router = APIRouter()


@router.get(
    "/rating",
    description="Get a specific user's rating for a product",
)
async def get_rating(owner_id: UUID, product_id: UUID):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                rating = Rating(owner_id, product_id).fetch(cursor)
                return rating.rating

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
