from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import authenticate
from database import get_db_connection
from model.user import User
from model.compra.compra import Compra
from model.product.product import Product

router = APIRouter()

class CompraRequest(BaseModel):
    products: List[UUID]

@router.post(
    "/compra",
    description="Purchase products",
)
async def post_compra(compra_request: CompraRequest, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = False  # Usar transacción para asegurar consistencia
                
                try:
                    # Verificar la disponibilidad de los productos (especialmente para los verificados)
                    for product_id in compra_request.products:
                        # Comprobar si es un producto verificado y tiene stock
                        check_query = """
                            SELECT vp_stock, vp_name 
                            FROM chopchop.verified_product 
                            WHERE vp_id = %s
                        """
                        cursor.execute(check_query, (product_id,))
                        verified_product = cursor.fetchone()
                        
                        if verified_product and verified_product[0] <= 0:
                            raise HTTPException(
                                status_code=400, 
                                detail=f"Product '{verified_product[1]}' is out of stock"
                            )
                        
                        # Comprobar si el producto de segunda mano existe y está disponible
                        if not verified_product:
                            secondhand_query = """
                                SELECT sp_name 
                                FROM chopchop.secondhand_product 
                                WHERE sp_id = %s
                            """
                            cursor.execute(secondhand_query, (product_id,))
                            secondhand_product = cursor.fetchone()
                            
                            if not secondhand_product:
                                # Intenta obtener algún nombre de producto para el error
                                cursor.execute(
                                    "SELECT COALESCE(vp_name, sp_name) FROM chopchop.verified_product vp LEFT JOIN chopchop.secondhand_product sp ON vp.vp_id = %s OR sp.sp_id = %s LIMIT 1",
                                    (product_id, product_id)
                                )
                                product_name = cursor.fetchone()
                                name_str = f" '{product_name[0]}'" if product_name and product_name[0] else ""
                                
                                raise HTTPException(
                                    status_code=404, 
                                    detail=f"Product{name_str} with ID {product_id} not found"
                                )
                    
                    # Crear la compra
                    compra = Compra(
                        user_id=user.id_,
                        products=compra_request.products
                    )
                    
                    compra_id = compra.insert(cursor, user)
                    conn.commit()
                    
                    return {"compra_id": compra_id}
                    
                except Exception as e:
                    conn.rollback()
                    if isinstance(e, HTTPException):
                        raise e
                    raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()
