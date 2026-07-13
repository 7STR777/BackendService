from app.db.config import settings
from app.db.database import AsyncORM
from app.services.schemas import UserResponse

from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from fastapi import Depends, status
from typing import Annotated
import jwt
from functools import wraps
from jwt.exceptions import PyJWTError
import bcrypt
from datetime import datetime, timedelta


security = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_jwt_token(payload: dict) -> str: 
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bad request"
    )
    to_encode = payload.copy()
    expire = datetime.now() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    try:
        token = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token
    except:
        raise credentials_exceptions

async def get_current_user_from_token(token: Annotated[str, Depends(security)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные данные для входа"
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = str(payload.get("sub"))
        if sub is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = await AsyncORM.get_user_by_id(int(sub))
    if user is None:
        raise credentials_exception
    if user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не существует"
        )
    return user


async def get_current_user(email: str, password:str):
    credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные данные"
        )
    try:
        user = await AsyncORM.get_user_from_email(email)
    except:
        raise credential_exception
    if not user:
        raise credential_exception
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise credential_exception
    if user.is_active == False:
        print('tut')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь неактивен"
        )
    return user


def admin_required(func):
    """Декоратор для проверки прав администратора"""
    @wraps(func)
    async def wrapper(*args, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)], **kwargs):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Вы не авторизованы"
            )
        
        role = await AsyncORM.get_role_by_id(current_user.role_id)
        if not role or role.lower() != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ ограничен. Требуются права администратора"
            )
        
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper
