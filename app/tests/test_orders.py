import pytest
from unittest.mock import AsyncMock, patch
from app.db.config import settings

@pytest.mark.asyncio
@patch("app.db.database.OrderData.create_order", new_callable=AsyncMock)
async def test_create_order_unauthorized(mock_register, client):
    """Тест успешной регистрации пользователя"""
    mock_register.return_value = True
    
    user_data = {
            "shipping_address": "г. Тест, ул. Тестовая, 8",
            "items": [
                {
                "product_id": 1,
                "quantity": 2
                }
            ]
        }
    
    response = await client.post(
        "/orders",
        json=user_data
    )
    
    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"
    
    data = response.json()

@pytest.mark.asyncio
@patch("app.services.security.jwt.decode")
@patch("app.db.database.AsyncORM.get_user_by_id", new_callable=AsyncMock)
@patch("app.db.database.AsyncORM.get_permissions_by_role_id", new_callable=AsyncMock)
@patch("app.db.database.OrderData.create_order", new_callable=AsyncMock)
@patch("app.db.database.ProductData.get_product_name", new_callable=AsyncMock)
@patch("app.db.database.ProductData.get_product_price", new_callable=AsyncMock)
async def test_create_order_success(
    mock_get_product_price,
    mock_get_product_name,
    mock_create_order,
    mock_get_permissions,
    mock_get_user_by_id,
    mock_jwt_decode,
    client
):
    """Тест успешного создания заказа"""
    mock_jwt_decode.return_value = {"sub": "1"}
    
    mock_user = AsyncMock()
    mock_user.user_id = 1
    mock_user.role_id = 1
    mock_user.is_active = True
    mock_get_user_by_id.return_value = mock_user
    
    mock_permission = AsyncMock()
    mock_permission.create_permission = True
    mock_get_permissions.return_value = [mock_permission]
    
    mock_new_order = AsyncMock()
    mock_new_order.order_id = 1
    mock_new_order.total_price = 1500
    mock_create_order.return_value = mock_new_order
    
    mock_get_product_name.return_value = "Тестовый товар"
    mock_get_product_price.return_value = 750
    
    order_data = {
        "shipping_address": "г. Тест, ул. Тестовая, 8",
        "items": [
            {
                "product_id": 1,
                "quantity": 2
            }
        ]
    }
    
    response = await client.post(
        "/orders",
        json=order_data,
        headers={"Authorization": "Bearer test_token_123"}
    )
    
    assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}"

@pytest.mark.asyncio
@patch("app.services.security.jwt.decode")
@patch("app.db.database.AsyncORM.get_user_by_id", new_callable=AsyncMock)
@patch("app.db.database.AsyncORM.get_permissions_by_role_id", new_callable=AsyncMock)
@patch("app.db.database.OrderData.create_order", new_callable=AsyncMock)
@patch("app.db.database.ProductData.get_product_name", new_callable=AsyncMock)
@patch("app.db.database.ProductData.get_product_price", new_callable=AsyncMock)
async def test_create_order_forbidden(
    mock_get_product_price,
    mock_get_product_name,
    mock_create_order,
    mock_get_permissions,
    mock_get_user_by_id,
    mock_jwt_decode,
    client
):
    """Тест успешного создания заказа"""
    mock_jwt_decode.return_value = {"sub": "1"}
    
    mock_user = AsyncMock()
    mock_user.user_id = 4
    mock_user.role_id = 4 #guest
    mock_user.is_active = True
    mock_get_user_by_id.return_value = mock_user
    
    mock_permission = AsyncMock()
    mock_permission.create_permission = False
    mock_get_permissions.return_value = [mock_permission]
    
    mock_new_order = AsyncMock()
    mock_new_order.order_id = 1
    mock_new_order.total_price = 1500
    mock_create_order.return_value = mock_new_order
    
    mock_get_product_name.return_value = "Тестовый товар"
    mock_get_product_price.return_value = 750
    
    order_data = {
        "shipping_address": "г. Тест, ул. Тестовая, 8",
        "items": [
            {
                "product_id": 1,
                "quantity": 2
            }
        ]
    }
    
    response = await client.post(
        "/orders",
        json=order_data,
        headers={"Authorization": "Bearer test_token_123"}
    )
    
    assert response.status_code == 403, f"Ожидался 403, получен {response.status_code}"
