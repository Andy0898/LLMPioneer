import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio

async def test_login_with_invalid_credentials(client: AsyncClient):
    """
    Test login with incorrect username and password.
    Expects a 401 Unauthorized error.
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistentuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Optionally, you can also check the content of the response
    json_response = response.json()
    assert json_response["detail"] == "Incorrect username or password"

async def test_login_with_missing_password(client: AsyncClient):
    """
    Test login with a missing password field.
    FastAPI should return a 422 Unprocessable Entity error.
    """
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

async def test_login_success(client: AsyncClient):
    """
    Test successful user login with valid credentials.
    Expects a 200 OK status and an access_token in the response.
    """
    # 模拟认证成功
    mock_auth_result = {
        "access_token": "mock_access_token_from_test",
        "token_type": "bearer",
        "roles": [{"code": "admin", "name": "管理员"}],
        "permissions": ["read", "write"]
    }

    with patch('app.services.auth_service.AuthService.authenticate', return_value=mock_auth_result):
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"
    assert "roles" in json_response
    assert "permissions" in json_response
