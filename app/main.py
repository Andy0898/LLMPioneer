import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.api.v1.endpoints.manage import router as manage_router
from app.api.v1.endpoints.sa import router as sa_router
from app.db.session import test_db_connection
from app.api.v1.endpoints.auth_controller import router as auth_router


def create_application() -> FastAPI:
    """
    创建FastAPI应用
    """
        # @app.on_event("startup")
    # async def startup_event():
    #     # 测试数据库连接
    #     if await test_db_connection():
    #         print("数据库连接成功！")
    #     else:
    #         print("警告：数据库连接失败！")
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # 应用启动时执行
        if await test_db_connection():
            print("数据库连接成功！")
        else:
            print("警告：数据库连接失败！")
        
        # 通过 yield 语句将控制权交给应用主体
        yield

        # 应用关闭时执行清理操作（如有需要）
        # 例如：await cleanup_resources()
    
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # 设置CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 注册路由
    app.include_router(auth_router, prefix="/auth", tags=["用户认证接口"])
    app.include_router(manage_router, prefix="/manage", tags=["后台管理接口"])
    app.include_router(sa_router, prefix="/sa", tags=["前端应用接口"])
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to LLM Pioneer API"}

    return app

app = create_application() 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=18000) 