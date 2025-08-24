import pytest_asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app

@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试客户端，直接测试应用实例
    无需启动外部Web服务
    """
    # 使用 ASGITransport 来测试应用实例
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

@pytest.fixture(autouse=True)
def mock_database():
    """
    自动模拟数据库连接，避免测试时连接真实数据库
    """
    with patch('app.services.auth.AuthService.authenticate') as mock_auth:
        # 模拟认证失败的情况
        mock_auth.return_value = None
        yield mock_auth

@pytest.fixture(autouse=True)
def mock_db_session():
    """
    模拟数据库会话
    """
    with patch('app.api.v1.deps.get_db') as mock_get_db:
        mock_session = AsyncMock()
        mock_get_db.return_value = mock_session
        yield mock_get_db