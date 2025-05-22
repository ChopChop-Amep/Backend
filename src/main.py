__version__ = "0.2.3"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api.product.get import router as product_get_router
from api.product.delete import router as product_delete_router
from api.product.post import router as product_post_router
from api.product.put import router as product_put_router

from api.products.get import router as products_get_router

from api.purchase.get import router as purchase_get_router
from api.purchase.post import router as purchase_post_router

from api.rating.get import router as rating_get_router
from api.rating.post import router as rating_post_router


api = FastAPI()

origins = [
    "*",
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.include_router(product_get_router)
api.include_router(product_delete_router)
api.include_router(product_post_router)
api.include_router(product_put_router)

api.include_router(products_get_router)

api.include_router(purchase_get_router)
api.include_router(purchase_post_router)

api.include_router(rating_get_router)
api.include_router(rating_post_router)
