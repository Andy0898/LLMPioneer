# 权限系统使用说明

## 概述

本系统实现了完整的基于角色的权限控制（RBAC），支持超级管理员和普通用户两种权限级别。

## 核心特性

### 1. 超级管理员 (super_admin)
- 拥有所有功能和数据的访问权限
- 不受任何权限限制
- 可以管理所有用户和资源

### 2. 普通用户
- 基于角色分配的具体权限
- 只能访问被授权的功能和数据
- 支持细粒度的权限控制

## 权限验证方式

### 1. 依赖注入方式

#### 基本权限验证
```python
from app.api.v1.deps import require_permissions

@router.get("/protected-endpoint")
async def protected_endpoint(
    current_user: UserModel = Depends(require_permissions(["user:read"]))
):
    return {"message": "访问成功"}
```

#### 超级管理员验证
```python
from app.api.v1.deps import require_super_admin

@router.get("/admin-only")
async def admin_only_endpoint(
    current_user: UserModel = Depends(require_super_admin())
):
    return {"message": "超级管理员访问成功"}
```

#### 数据访问权限验证
```python
from app.api.v1.deps import check_data_access_permission

@router.get("/document/{document_id}")
async def access_document(
    document_id: int,
    current_user: UserModel = Depends(
        check_data_access_permission(resource_owner_id=document_id)
    )
):
    return {"message": "文档访问成功"}
```

### 2. 服务层权限检查

#### 使用 PermissionManager
```python
from app.services.permission_manager import PermissionManager

class SomeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.permission_manager = PermissionManager(db)
    
    async def some_method(self, user_id: int, required_permission: str):
        # 检查权限
        if not await self.permission_manager.check_permission(user_id, required_permission):
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 执行业务逻辑
        pass
```

## 权限数据结构

### 权限格式
权限采用 `资源:操作` 的格式，例如：
- `user:read` - 用户读取权限
- `user:create` - 用户创建权限
- `document:delete` - 文档删除权限
- `system:admin` - 系统管理权限

### 角色权限关联
```python
# 角色模型
class RoleModel(Base):
    code: str  # 角色编码，如 "super_admin", "user_manager"
    name: str  # 角色名称

# 权限模型
class FunctionPermissionModel(Base):
    value: str  # 权限值，如 "user:read"
    title: str  # 权限标题

# 角色权限关联
class RolePermissionModel(Base):
    role_id: int
    func_per_id: int
```

## 使用示例

### 1. 创建超级管理员角色
```sql
INSERT INTO t_sys_role (code, name, org_id, create_by) 
VALUES ('super_admin', '超级管理员', 1, 'system');
```

### 2. 创建普通角色
```sql
INSERT INTO t_sys_role (code, name, org_id, create_by) 
VALUES ('user_manager', '用户管理员', 1, 'system');
```

### 3. 分配权限
```sql
-- 为用户管理员分配用户管理权限
INSERT INTO t_sys_role_func_per (role_id, func_per_id) 
SELECT r.id, p.id 
FROM t_sys_role r, t_sys_function_permission p 
WHERE r.code = 'user_manager' AND p.value IN ('user:read', 'user:create', 'user:update');
```

### 4. 在控制器中使用
```python
@router.get("/users")
async def get_users(
    current_user: UserModel = Depends(require_permissions(["user:read"]))
):
    # 只有拥有 user:read 权限的用户才能访问
    return {"users": []}

@router.post("/users")
async def create_user(
    current_user: UserModel = Depends(require_permissions(["user:create"]))
):
    # 只有拥有 user:create 权限的用户才能访问
    return {"message": "用户创建成功"}
```

## 权限检查流程

1. **用户登录** → 获取角色和权限信息
2. **API访问** → 检查用户权限
3. **权限验证** → 超级管理员直接通过，普通用户检查具体权限
4. **访问控制** → 根据权限决定是否允许访问

## 最佳实践

### 1. 权限粒度
- 建议使用细粒度的权限控制
- 权限命名要清晰明确
- 避免过于复杂的权限组合

### 2. 性能优化
- 权限信息在登录时一次性获取
- 使用缓存减少数据库查询
- 避免在每次请求时重复查询权限

### 3. 安全考虑
- 前端权限控制仅用于用户体验
- 后端必须进行权限验证
- 定期审查权限分配

### 4. 错误处理
- 权限不足时返回明确的错误信息
- 记录权限验证失败的日志
- 提供友好的用户提示

## 常见问题

### Q: 如何添加新的权限？
A: 在 `t_sys_function_permission` 表中添加新的权限记录，然后分配给相应的角色。

### Q: 超级管理员可以修改自己的权限吗？
A: 可以，但建议保留超级管理员角色的完整性，避免权限丢失。

### Q: 如何实现动态权限？
A: 可以通过配置文件或数据库配置来实现动态权限，但需要确保权限验证的安全性。

### Q: 权限缓存如何更新？
A: 当权限发生变化时，需要清除相关用户的权限缓存，确保权限及时生效。
