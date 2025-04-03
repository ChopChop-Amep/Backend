__version__ = "0.1.7"

from fastapi import FastAPI

from api.product.get import router as product_get_router
from api.product.delete import router as product_delete_router
from api.product.post import router as product_post_router
from api.products.get import router as products_get_router
from api.product.put import router as product_put_router


api = FastAPI()

api.include_router(product_get_router)
api.include_router(product_delete_router)
api.include_router(product_post_router)
api.include_router(product_put_router)

api.include_router(products_get_router)
