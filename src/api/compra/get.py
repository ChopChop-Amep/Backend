from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from auth import authenticate
from database import get_db_connection
from model.user import User
from model.compra.compra import Compra

router = APIRouter()


@router.get(
    "/compra/{compra_id}/factura",
    description="Generar factura de una compra",
)
async def get_factura(compra_id: UUID, user: User = Depends(authenticate)):
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                # Obtener la compra
                compra = Compra.get_compra(cursor, compra_id)

                # Verificar que el usuario sea el propietario de la compra
                if str(compra.user_id) != str(user.id_):
                    # Verificar si es admin (los admins pueden ver todas las facturas)
                    check_admin_query = """
                        SELECT * FROM chopchop.admin WHERE a_id = %s
                    """
                    cursor.execute(check_admin_query, (user.id_,))
                    is_admin = cursor.fetchone() is not None

                    if not is_admin:
                        raise HTTPException(
                            status_code=403,
                            detail="You can only access your own invoices"
                        )

                # Generar la factura
                factura = compra.extreure_factura(cursor)
                return factura

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()
