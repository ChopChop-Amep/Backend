__version__ = "0.1.1"

from fastapi import FastAPI

from api.product.post import router as product_post_router

api = FastAPI()
api.include_router(product_post_router)
