import os
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from model.user import User, Particular, Professional, Enterprise, Admin

SECRET_KEY = os.getenv("SECRET_KEY", "Secret key missing!!")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        metadata = payload.get("user_metadata")
        type = User.Type(metadata.get("type"))

        match type:
            case User.Type.PARTICULAR:
                return Particular(
                    id=UUID(payload.get("sub")),
                    name=metadata.get("name"),
                    surname=metadata.get("surname"),
                )

            case User.Type.PROFESSIONAL:
                return Professional(
                    id=UUID(payload.get("sub")),
                    name=metadata.get("name"),
                    surname=metadata.get("surname"),
                    nif=metadata.get("nif"),
                )

            case User.Type.ENTERPRISE:
                return Enterprise(
                    id=UUID(payload.get("sub")),
                    name=metadata.get("name"),
                    surname=metadata.get("surname"),
                    nif=metadata.get("nif"),
                )

            case User.Type.ADMIN:
                return Admin(
                    id=UUID(payload.get("sub")),
                    name=metadata.get("name"),
                    surname=metadata.get("surname"),
                )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token could not be validated",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate(token: str = Depends(oauth2_scheme)):
    return verify_jwt_token(token)
