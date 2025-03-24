__version__ = "0.1.3"

from fastapi import FastAPI

from api.product.get import router as product_get_router
from api.product.delete import router as product_delete_router

api = FastAPI()

api.include_router(product_get_router)
api.include_router(product_delete_router)
