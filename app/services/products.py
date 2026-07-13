from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Annotated

from app.services.schemas import UserResponse, UpdateProduct, CreateProduct, UpdateFieldsOfProduct, ProductResponse, UpdateProductResponse
from app.db.database import AsyncORM, ProductData
from app.services.security import get_current_user_from_token


product_router = APIRouter()

@product_router.get("/products")
async def show_all_products(current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Показывает все продукты.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permissions = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'products')
    if permissions[0].read_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )
    products = await ProductData.get_all_products()
    if products is None:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail='Список пуст'
        )
    return products

@product_router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(crpr: CreateProduct, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Создает продукт
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permissions = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'products')
    if permissions[0].create_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )
    try:
        await ProductData.create_product(crpr.product_name, crpr.price, crpr.amount)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить товар"
        )
    return ProductResponse(
        message=f'Товар {crpr.product_name} был успешно добавлен!',
        items=[
            CreateProduct(
                product_name=crpr.product_name,
                price=crpr.price,
                amount=crpr.amount
            )
        ]
    )

@product_router.get("/products/{product_id}")
async def show_product(product_id: int, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Показывает карточку продукта.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    product = await ProductData.get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Список пуст'
        )
    return product


@product_router.patch("/products/{product_id}")
async def update_fields_product(product_id: int, updatepr: UpdateFieldsOfProduct, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Частично обновляет поля продукта (PATCH)
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permissions = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'products')
    if permissions[0].update_permission == False and permissions[0].update_all_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )
    
    update_data = updatepr.model_dump(exclude_none=True, by_alias=False)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления"
        )

    updated_product = await ProductData.update_fields_of_product(product_id, update_data)

    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продукт не найден"
        )
    return {
        "product_id":product_id,
        **update_data 
    }

@product_router.put("/products/{product_id}")
async def update_product(product_id: int, updatepr: UpdateProduct, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Обновление продукта целиком
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permissions = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'products')
    if permissions[0].update_permission == False and permissions[0].update_all_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )
    await ProductData.update_product(product_id, updatepr.product_name, updatepr.amount, updatepr.price)
    return UpdateProductResponse(
        message="Информация о продукте была обновлена!",
        items=[
            UpdateProduct(
                product_name=updatepr.product_name,
                amount=updatepr.amount,
                price=updatepr.price
            )
        ]
    )


@product_router.delete("/products/{product_id}")
async def delete_product(product_id: int, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Удаляет продукт по product_id
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permissions = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'products')
    if permissions[0].delete_permission == False and permissions[0].delete_all_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )
    await ProductData.delete_product(product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":f"Продукт с id={product_id} был удален"
        }
    )
    
