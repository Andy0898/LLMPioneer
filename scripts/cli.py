import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import typer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from init_admin import init_admin

init_app = typer.Typer()

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@init_app.command()
def create_admin():
    """创建超级管理员用户和初始化权限"""
    async def run():
        async for db in get_db():
            try:
                result = await init_admin(db)
                typer.echo("超级管理员创建成功！")
                typer.echo(f"用户名: {result['admin_user'].user_name}")
                typer.echo(f"密码: admin123")
                typer.echo(f"角色: {result['admin_role'].name}")
                typer.echo(f"权限数量: {len(result['permissions'])}")
            except Exception as e:
                typer.echo(f"错误: {str(e)}")
                raise e
    
    asyncio.run(run())

if __name__ == "__main__":
    init_app() 