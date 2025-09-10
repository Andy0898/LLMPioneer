# import sys
# from pathlib import Path

# 将项目根目录添加到 Python 路径
# ROOT_DIR = Path(__file__).resolve().parent.parent
# sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import CONFIG as settings
from app.api.v1.endpoints.manage import router as manage_router
from app.api.v1.endpoints.sa import router as sa_router
from app.api.v1.endpoints.auth_controller import router as auth_router
from app.db.session import test_db_connection


def create_application() -> FastAPI:
    """
    创建FastAPI应用实例
    """
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """应用生命周期管理"""
        # 应用启动时执行
        try:
            if await test_db_connection():
                print("✅ 数据库连接成功！")
            else:
                print("⚠️  警告：数据库连接失败！")
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
        
        yield
        
        # 应用关闭时执行清理操作
        print("🔄 应用正在关闭，清理资源...")
    
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="LLM Pioneer - 智能助理系统API",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 配置CORS中间件
    _configure_cors(app)
    
    # 注册API路由
    _register_routes(app)
    
    # 注册根路径
    _register_root_endpoint(app)
    
    return app


def _configure_cors(app: FastAPI) -> None:
    """配置CORS中间件"""
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _register_routes(app: FastAPI) -> None:
    """注册API路由"""
    api_router = APIRouter()
    
    # 注册各个模块的路由
    api_router.include_router(
        auth_router, 
        prefix="/auth", 
        tags=["用户认证接口"]
    )
    api_router.include_router(
        manage_router, 
        prefix="/manage", 
        tags=["后台管理接口"]
    )
    api_router.include_router(
        sa_router, 
        prefix="/sa", 
        tags=["前端应用接口"]
    )
    
    # 将聚合后的路由统一加上 /api/v1 前缀
    app.include_router(api_router, prefix=settings.API_V1_STR)


def _register_root_endpoint(app: FastAPI) -> None:
    """注册根路径端点"""
    @app.get("/", tags=["系统信息"])
    async def root():
        return {
            "message": "Welcome to LLM Pioneer API",
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }


# 创建应用实例
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    # 从配置文件读取端口，而不是硬编码
    port = settings.port
    host = settings.server.host
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        reload=True,  # 开发环境启用热重载
        log_level="info"
    )