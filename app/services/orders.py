from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Annotated

from app.services.schemas import OrderResponse, UserResponse, OrderCreate, OrderItemResponse
from app.db.database import AsyncORM, OrderData, ProductData
from app.services.security import get_current_user_from_token

from datetime import datetime

order_router = APIRouter()

@order_router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """Создание заказа"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permisssion = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'orders')
    if permisssion[0].create_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )

    if len(order_data.shipping_address) < 5 or order_data.shipping_address is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неправильно указан адрес доставки"
        )
    
    if len(order_data.items) == 0 or order_data.items is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Список корзины пуст"
        )
    
    try:
        items_for_create = [
            {"product_id": item.product_id, "quantity": item.quantity}
            for item in order_data.items
        ]
        
        new_order = await OrderData.create_order(
            user_id=current_user.user_id,
            shipping_address=order_data.shipping_address,
            items_data=items_for_create
        )

        return OrderResponse(
            order_id=new_order.order_id,
            created_at=datetime.now(),
            status="pending",
            total_price=new_order.total_price,
            shipping_address=order_data.shipping_address,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    product_name=await ProductData.get_product_name(item.product_id),
                    quantity=item.quantity,
                    price_at_time=await ProductData.get_product_price(item.product_id)
                )
                for item in order_data.items
            ]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@order_router.get("/orders/me")
async def get_orders(current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """Показывает все заказы пользователя"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permisssion = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'orders')
    if permisssion[0].read_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )
    try: 
        orders = await OrderData.get_orders_by_user_id(current_user.user_id)
        
        if orders is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Список корзины пуст"
            )
        return orders
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@order_router.get("/order/{order_id}")
async def get_order_detail(
    order_id: int,
    current_user: Annotated[
        UserResponse,
        Depends(get_current_user_from_token)
    ]
):
    permission = await AsyncORM.get_permissions_by_role_id(
        current_user.role_id,
        "orders"
    )

    if not permission[0].read_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )

    role_name = await AsyncORM.get_role_by_id(current_user.role_id)

    # Если не админ — проверяем владельца заказа
    if role_name != "admin":
        is_owner = await OrderData.check_ownership_of_order(
            current_user.user_id,
            order_id
        )

        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому заказу"
            )

    order_detail = await OrderData.get_order_details(order_id)

    if not order_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )

    return order_detail
    
@order_router.put("/orders/{order_id}/status")
async def change_status_of_order(order_id: int, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """Изменение статус заказа"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы"
        )
    permisssion = await AsyncORM.get_permissions_by_role_id(current_user.role_id, 'orders')
    if permisssion[0].read_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )