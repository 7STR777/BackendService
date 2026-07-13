import pytest
from unittest.mock import AsyncMock, patch
from app.db.config import settings

@pytest.mark.asyncio
@patch("app.db.database.AsyncORM.register_user", new_callable=AsyncMock)
async def test_registration_success(mock_register, client):
    """Тест успешной регистрации пользователя"""
    mock_register.return_value = True
    
    user_data = {
        "surname": "Иванов",
        "name": "Иван",
        "email": "ivan@test.com",
        "password": "TestPassword123",
        "repeat_password": "TestPassword123",
        "role_id": 1,
        "is_active": True
    }
    
    response = await client.post(
        "/auth/registration",
        json=user_data
    )
    
    assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}"
    
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Аккаунт успешно создан!"
    assert data["data"][0]["email"] == user_data["email"]
    assert data["data"][0]["surname"] == user_data["surname"]
    assert data["data"][0]["name"] == user_data["name"]

@pytest.mark.asyncio
@patch("app.db.database.AsyncORM.register_user", new_callable=AsyncMock)
async def test_registration_password_mismatch(mock_register, client):
    """Тест регистрации с несовпадающими паролями"""
    mock_register.return_value = True
    
    user_data = {
        "surname": "Иванов",
        "name": "Иван",
        "email": "ivan@test.com",
        "password": "TestPassword123",
        "repeat_password": "DifferentPassword",
        "role_id": 1,
        "is_active": True
    }
    
    response = await client.post(
        "/auth/registration",
        json=user_data
    )
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
    
    data = response.json()
    assert data["detail"] == "Пароли не совпадают"

@pytest.mark.asyncio
@patch("app.db.database.AsyncORM.register_user", new_callable=AsyncMock)
async def test_registration_invalid_email(mock_register, client):
    """Тест регистрации с неверным форматом email"""
    mock_register.return_value = True
    
    user_data = {
        "surname": "Иванов",
        "name": "Иван",
        "email": "invalid-email",
        "password": "TestPassword123",
        "repeat_password": "TestPassword123",
        "role_id": 1,
        "is_active": True
    }
    
    response = await client.post(
        "/auth/registration",
        json=user_data
    )
    
    assert response.status_code == 400, f"Ожидался 400, получен {response.status_code}"
    
    data = response.json()
    assert data["detail"] == "Неправильный формат почты"

@pytest.mark.asyncio
@patch("app.db.database.AsyncORM.register_user", new_callable=AsyncMock)
async def test_registration_db_error(mock_register, client):
    """Тест регистрации при ошибке базы данных"""
    mock_register.side_effect = Exception("Database error")
    
    user_data = {
        "surname": "Иванов",
        "name": "Иван",
        "email": "ivan@test.com",
        "password": "TestPassword123",
        "repeat_password": "TestPassword123",
        "role_id": 1,
        "is_active": True
    }
    
    response = await client.post(
        "/auth/registration",
        json=user_data
    )
    
    assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}"
    
    data = response.json()
    assert data["detail"] == "Произошла ошибка"

@pytest.mark.asyncio
@patch("app.services.security.get_current_user", new_callable=AsyncMock)
async def test_login_success(mock_get_user, client):
    """Тест успешного входа в систему"""
    mock_user = AsyncMock()
    mock_user.user_id = 1
    mock_user.role_id = 1
    mock_get_user.return_value = mock_user

    login_data = {
        "username": "admin@mail.com",
        "password": "admin"
    }

    response = await client.post(
        "/auth/login",
        data=login_data,  
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    
    data = response.json()
    assert "access_token" in data, "В ответе отсутствует access_token"
    assert data["token_type"] == "bearer", f"Ожидался bearer, получен {data['token_type']}"
    assert data["access_token"] is not None, "access_token не должен быть пустым"

@pytest.mark.asyncio
@patch("app.services.security.get_current_user", new_callable=AsyncMock)
async def test_login_invalid_credentials(mock_get_user, client):
    """Тест входа с неверными учетными данными"""
    from fastapi.exceptions import HTTPException
    from fastapi import status
    
    mock_get_user.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный email или пароль"
    )

    login_data = {
        "username": "wrong@mail.com",
        "password": "wrongpassword"
    }

    response = await client.post(
        "/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"

@pytest.mark.asyncio
@patch("app.services.security.jwt.decode")
@patch("app.db.database.AsyncORM.get_user_by_id", new_callable=AsyncMock)
async def test_logout_success(mock_get_user_by_id, mock_jwt_decode, client):
    """Тест успешного выхода из системы"""
    mock_jwt_decode.return_value = {"sub": "1"}
    
    mock_user = AsyncMock()
    mock_user.user_id = 1
    mock_user.email = "test@test.com"
    mock_user.surname = "Test"
    mock_user.name = "User"
    mock_user.role_id = 1
    mock_user.is_active = True
    mock_get_user_by_id.return_value = mock_user

    response = await client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer test_token_123"}
    )

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    
    data = response.json()
    assert data["success"] is True, "success должен быть True"
    assert data["message"] == "Вы успешно вышли из системы"
    
    mock_jwt_decode.assert_called_once_with(
        "test_token_123", 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    mock_get_user_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_logout_without_token(client):
    """Тест выхода без токена"""
    response = await client.post("/auth/logout")

    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"


@pytest.mark.asyncio
@patch("app.db.database.AsyncORM.register_user", new_callable=AsyncMock)
async def test_registration_missing_fields(mock_register, client):
    """Тест регистрации с отсутствующими полями"""
    mock_register.return_value = True
    
    user_data = {
        "surname": "Иванов",
        "name": "Иван",
        "email": "ivan@test.com",
    }
    
    response = await client.post(
        "/auth/registration",
        json=user_data
    )
    
    assert response.status_code == 422, f"Ожидался 422, получен {response.status_code}"


@pytest.mark.asyncio
@patch("app.services.security.get_current_user", new_callable=AsyncMock)
async def test_login_missing_username(mock_get_user, client):
    """Тест входа без username"""
    login_data = {
        "password": "admin"
    }

    response = await client.post(
        "/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 422, f"Ожидался 422, получен {response.status_code}"

@pytest.mark.asyncio
@patch("app.services.security.get_current_user", new_callable=AsyncMock)
async def test_login_missing_password(mock_get_user, client):
    """Тест входа без password"""
    login_data = {
        "username": "admin@mail.com"
    }

    response = await client.post(
        "/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 422, f"Ожидался 422, получен {response.status_code}"