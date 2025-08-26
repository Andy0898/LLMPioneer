import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine # Import the engine

@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试客户端，直接测试应用实例
    无需启动外部Web服务
    """
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

    # 确保数据库引擎在所有测试结束后被正确关闭
    await engine.dispose()
