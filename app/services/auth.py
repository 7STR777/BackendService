from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.services.schemas import UserCreate, RegistrationResponse, RegistrationDataResponse, UserResponse
from app.db.database import AsyncORM
from app.services.security import create_jwt_token, get_current_user, get_current_user_from_token
from app.services.encrypting import encrypt_password, email_validation
from typing import Annotated
from starlette import status

auth_router = APIRouter()

@auth_router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(user: UserCreate):
    """
    Регистрация пользователя в базе данных с уникальным email
    """
    if user.password != user.repeat_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пароли не совпадают"
        )
    hashed_password = encrypt_password(user.password)
    email = email_validation(user.email)
    if email is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неправильный формат почты"
        )
    
    try:
        await AsyncORM.register_user(
            user.surname,
            user.name,
            hashed_password,
            user.email,
            user.is_active
        )
        return RegistrationResponse(
            status='success',
            message='Аккаунт успешно создан!',
            data=[
                RegistrationDataResponse(
                    surname=user.surname,
                    name=user.name,
                    email=user.email,
                    password=user.password,
                    role_id=user.role_id,
                    is_active=user.is_active
                )
            ]
        )
    except:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Произошла ошибка"
    )

@auth_router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await get_current_user(
        form_data.username, 
        form_data.password
    )
    token = create_jwt_token({
        "sub": str(user.user_id),
        "role": str(user.role_id),
    })
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": token,
            "token_type": "bearer",
        }
    )
        

@auth_router.post("/logout")
async def logout(current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    if current_user:
        return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success":True,
            "message":"Вы успешно вышли из системы"
        }
    )
    raise HTTPException(
        status_code=401,
        detail='Вы неавторизованы'
    )
