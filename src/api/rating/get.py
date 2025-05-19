from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException

from database import get_db_connection
from model.rating import Rating

router = APIRouter()


@router.get(
    "/rating/{rating_id}",
    description="Get a specific rating by ID",
)
async def get_rating(rating_id: UUID):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                rating = Rating()
                return rating.fetch(cursor, rating_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


@router.get(
    "/rating/product/{product_id}",
    description="Get rating for a specific product",
)
async def get_product_rating(product_id: UUID):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                rating = Rating.get_product_rating(cursor, product_id)
                if not rating:
                    raise HTTPException(
                        status_code=404, detail="Rating not found")
                return rating

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
