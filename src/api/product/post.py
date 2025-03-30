from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from psycopg import sql

from auth import authenticate
from database import get_db_connection
from model.product import NewProduct, ProductType

router = APIRouter()


@router.post(
    "/product",
    description="Create a new product",
)
async def post_product(product: NewProduct, user_id: UUID = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = (
                    False  # Utilitzar una transacció ja que hi ha 2 insercions
                )

                try:
                    insert_product_query = sql.SQL("""
                        INSERT INTO chopchop.product_id DEFAULT VALUES
                        RETURNING product_id
                    """)
                    cursor.execute(insert_product_query)
                    product_id = cursor.fetchone()[0]

                    match product.type_:
                        case ProductType.VERIFIED:
                            insert_verified_query = sql.SQL("""
                                INSERT INTO chopchop.verified_product (
                                    vp_id, 
                                    vp_owner, 
                                    vp_sku, 
                                    vp_name, 
                                    vp_description, 
                                    vp_stock, 
                                    vp_price, 
                                    vp_image, 
                                    vp_category
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """)
                            cursor.execute(
                                insert_verified_query,
                                (
                                    product_id,
                                    user_id,
                                    product.sku,
                                    product.name,
                                    product.description,
                                    product.stock,
                                    product.price,
                                    product.image,
                                    product.category.value,
                                ),
                            )

                        case ProductType.SECONDHAND:
                            insert_secondhand_query = sql.SQL("""
                                INSERT INTO chopchop.secondhand_product (
                                    sp_id, 
                                    sp_owner, 
                                    sp_name, 
                                    sp_description, 
                                    sp_price, 
                                    sp_image, 
                                    sp_category
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """)
                            cursor.execute(
                                insert_secondhand_query,
                                (
                                    product_id,
                                    user_id,
                                    product.name,
                                    product.description,
                                    product.price,
                                    product.image,
                                    product.category.value,
                                ),
                            )

                    conn.commit()  # Cometre la transacció si tot ha anat bé
                    return product_id

                except Exception as e:
                    conn.rollback()  # Fer rollback si cap inserció falla
                    raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
