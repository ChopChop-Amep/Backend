from fastapi import APIRouter

from model import VerifiedProduct, SecondHandProduct

router = APIRouter()


@router.post("/product/verified", description="Post a new verified product to the database")
async def post_verified_product(product: VerifiedProduct):
    return {"message": "Product created", "product": product}


@router.post("/product/secondhand", description="Post a new second hand product to the database")
async def post_secondhand_product(product: SecondHandProduct):
    return {"message": "Product created", "product": product}
