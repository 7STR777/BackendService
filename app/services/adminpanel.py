from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Annotated

from app.services.schemas import UserResponse, UpdateFieldOfPermission, UpdateFieldOfPermissionResponse, OrderResponse, OrderItemResponse
from app.db.database import AdminPanel, ProductData, OrderData, AsyncORM
from app.services.security import get_current_user_from_token, admin_required
from datetime import datetime


adminpanel_router = APIRouter()

@adminpanel_router.get("/showallpermissions")
@admin_required
async def get_all_permissions(current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Показывает все разрешения для пользователей
    """
    permissions = await AdminPanel.get_all_permissions()
    if permissions[0].read_all_permission == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа"
        )
    return permissions

@adminpanel_router.patch("/updatepermission")
@admin_required
async def update_field_of_permission(access_roles_rules_id: int, updateper: UpdateFieldOfPermission, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """
    Обновляет поля разрешений
    """
    update_data = updateper.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нет данных для обновления"
        )
    await AdminPanel.update_fields_of_permission(access_roles_rules_id, update_data)
    return UpdateFieldOfPermissionResponse(
        message='Разрешения были обновлены',
        permissions=[
            UpdateFieldOfPermission(
                role_id=updateper.role_id,
                business_element_id=updateper.business_element_id,
                read_permission=updateper.read_permission,
                read_all_permission=updateper.read_all_permission,
                create_permission=updateper.create_permission,
                update_permission=updateper.update_permission,
                update_all_permission=updateper.update_all_permission,
                delete_permission=updateper.delete_permission,
                delete_all_permission=updateper.delete_all_permission
            )
        ]
    ) 

@adminpanel_router.delete("/deletepermission/{access_roles_rules_id}")
@admin_required
async def delete_permission(access_roles_rules_id: int, current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """Удаляет разрешение"""
    try:
        await AdminPanel.delete_permission(access_roles_rules_id)
    except:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Произошла ошибка при удалении"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":f"Разрешение с id={access_roles_rules_id} было удалено"
        }
    )

@adminpanel_router.get("/orders")
@admin_required
async def get_all_orders(current_user: Annotated[UserResponse, Depends(get_current_user_from_token)]):
    """Показывает все заказы пользователей"""
    try:
        orders = await AdminPanel.get_all_orders()

        if not orders:
            return {
                "status": "success",
                "message": "Заказов нет",
                "data": [],
                "total": 0
            }
        
        orders_response = []
        for order in orders:
            user = await AsyncORM.get_user_by_id(order.user_id)
            
            orders_response.append({
                "order_id": order.order_id,
                "created_at": order.created_at,
                "status": order.status,
                "total_price": order.total_price,
                "shipping_address": order.shipping_address,
                "user": {
                    "user_id": user.user_id if user else None,
                    "email": user.email if user else None,
                    "name": user.name if user else None,
                    "surname": user.surname if user else None
                },
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "price_at_time": item.price_at_time
                    }
                    for item in order.items
                ]
            })
        
        return {
            "status": "success",
            "message": f"Найдено {len(orders)} заказов",
            "data": orders_response,
            "total": len(orders)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )