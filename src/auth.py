import os
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from model.user import User

SECRET_KEY = os.getenv("SECRET_KEY", "Secret key missing!!")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        type_ = User.Type(payload.get("type"))
        nif = None

        if type_ in User.VERIFIED_TYPES:
            nif = payload.get("nif")

        user = User(
            id_=UUID(payload.get("sub")),
            name=payload.get("name"),
            surname=payload.get("surname"),
            type_=type_,
            nif=nif,
        )

        return user

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token could not be validated",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate(token: str = Depends(oauth2_scheme)):
    return verify_jwt_token(token)
