# tests/unit/test_permission_system.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.permission_manager import PermissionManager
from app.core.security import check_permission, get_user_permission_level
from app.db.models import RoleModel, FunctionPermissionModel

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_role_service():
    return MagicMock()

@pytest.fixture
def permission_manager(mock_db, mock_role_service):
    manager = PermissionManager(mock_db)
    manager.role_service = mock_role_service
    return manager

@pytest.fixture
def super_admin_role():
    role = MagicMock()
    role.code = "super_admin"
    role.name = "超级管理员"
    return role

@pytest.fixture
def normal_role():
    role = MagicMock()
    role.code = "user_manager"
    role.name = "用户管理员"
    return role

@pytest.fixture
def user_permissions():
    return [
        MagicMock(value="user:read"),
        MagicMock(value="user:create"),
        MagicMock(value="document:read")
    ]

class TestPermissionManager:
    """权限管理器测试"""
    
    async def test_is_super_admin_true(self, permission_manager, super_admin_role):
        """测试超级管理员检测 - 是超级管理员"""
        roles = [super_admin_role]
        result = permission_manager._is_super_admin(roles)
        assert result is True
    
    async def test_is_super_admin_false(self, permission_manager, normal_role):
        """测试超级管理员检测 - 不是超级管理员"""
        roles = [normal_role]
        result = permission_manager._is_super_admin(roles)
        assert result is False
    
    async def test_get_user_permission_info_super_admin(
        self, permission_manager, mock_role_service, super_admin_role
    ):
        """测试获取超级管理员权限信息"""
        mock_role_service.get_user_roles.return_value = [super_admin_role]
        
        result = await permission_manager.get_user_permission_info(1)
        
        assert result["is_super_admin"] is True
        assert result["can_access_all"] is True
        assert result["permissions"] == ["*"]
        assert result["permission_level"] == "super_admin"
    
    async def test_get_user_permission_info_normal_user(
        self, permission_manager, mock_role_service, normal_role, user_permissions
    ):
        """测试获取普通用户权限信息"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        mock_role_service.get_role_permissions.return_value = user_permissions
        
        result = await permission_manager.get_user_permission_info(1)
        
        assert result["is_super_admin"] is False
        assert result["can_access_all"] is False
        assert result["permissions"] == ["user:read", "user:create", "document:read"]
        assert result["permission_level"] == "normal_user"
    
    async def test_check_permission_super_admin(
        self, permission_manager, mock_role_service, super_admin_role
    ):
        """测试超级管理员权限检查"""
        mock_role_service.get_user_roles.return_value = [super_admin_role]
        
        result = await permission_manager.check_permission(1, "any:permission")
        assert result is True
    
    async def test_check_permission_normal_user_has_permission(
        self, permission_manager, mock_role_service, normal_role, user_permissions
    ):
        """测试普通用户权限检查 - 有权限"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        mock_role_service.get_role_permissions.return_value = user_permissions
        
        result = await permission_manager.check_permission(1, "user:read")
        assert result is True
    
    async def test_check_permission_normal_user_no_permission(
        self, permission_manager, mock_role_service, normal_role, user_permissions
    ):
        """测试普通用户权限检查 - 无权限"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        mock_role_service.get_role_permissions.return_value = user_permissions
        
        result = await permission_manager.check_permission(1, "admin:all")
        assert result is False
    
    async def test_check_permissions_super_admin(
        self, permission_manager, mock_role_service, super_admin_role
    ):
        """测试超级管理员多权限检查"""
        mock_role_service.get_user_roles.return_value = [super_admin_role]
        
        required_permissions = ["user:read", "admin:all", "system:config"]
        result = await permission_manager.check_permissions(1, required_permissions)
        
        expected = {perm: True for perm in required_permissions}
        assert result == expected
    
    async def test_check_permissions_normal_user(
        self, permission_manager, mock_role_service, normal_role, user_permissions
    ):
        """测试普通用户多权限检查"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        mock_role_service.get_role_permissions.return_value = user_permissions
        
        required_permissions = ["user:read", "admin:all", "document:read"]
        result = await permission_manager.check_permissions(1, required_permissions)
        
        expected = {
            "user:read": True,
            "admin:all": False,
            "document:read": True
        }
        assert result == expected
    
    async def test_validate_data_access_super_admin(
        self, permission_manager, mock_role_service, super_admin_role
    ):
        """测试超级管理员数据访问权限"""
        mock_role_service.get_user_roles.return_value = [super_admin_role]
        
        result = await permission_manager.validate_data_access(
            user_id=1,
            resource_owner_id=999,
            resource_org_id=888
        )
        assert result is True
    
    async def test_validate_data_access_own_resource(
        self, permission_manager, mock_role_service, normal_role
    ):
        """测试用户访问自己的资源"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        
        result = await permission_manager.validate_data_access(
            user_id=1,
            resource_owner_id=1,
            resource_org_id=888
        )
        assert result is True
    
    async def test_validate_data_access_org_resource(
        self, permission_manager, mock_role_service, normal_role
    ):
        """测试用户访问同组织的资源"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        
        result = await permission_manager.validate_data_access(
            user_id=1,
            resource_owner_id=999,
            resource_org_id=100,
            user_org_id=100
        )
        assert result is True
    
    async def test_validate_data_access_denied(
        self, permission_manager, mock_role_service, normal_role
    ):
        """测试用户访问被拒绝的资源"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        
        result = await permission_manager.validate_data_access(
            user_id=1,
            resource_owner_id=999,
            resource_org_id=888,
            user_org_id=100
        )
        assert result is False

class TestSecurityFunctions:
    """安全函数测试"""
    
    def test_check_permission_super_admin(self):
        """测试权限检查函数 - 超级管理员"""
        result = check_permission("any:permission", ["user:read"], is_super_admin=True)
        assert result is True
    
    def test_check_permission_normal_user_has_permission(self):
        """测试权限检查函数 - 普通用户有权限"""
        result = check_permission("user:read", ["user:read", "user:create"], is_super_admin=False)
        assert result is True
    
    def test_check_permission_normal_user_no_permission(self):
        """测试权限检查函数 - 普通用户无权限"""
        result = check_permission("admin:all", ["user:read", "user:create"], is_super_admin=False)
        assert result is False
    
    def test_get_user_permission_level_super_admin(self, super_admin_role):
        """测试获取用户权限级别 - 超级管理员"""
        roles = [super_admin_role]
        user_permissions = ["user:read", "user:create"]
        
        result = get_user_permission_level(roles, user_permissions)
        
        assert result["is_super_admin"] is True
        assert result["can_access_all"] is True
        assert result["available_permissions"] == ["*"]
        assert result["role_codes"] == ["super_admin"]
    
    def test_get_user_permission_level_normal_user(self, normal_role):
        """测试获取用户权限级别 - 普通用户"""
        roles = [normal_role]
        user_permissions = ["user:read", "user:create"]
        
        result = get_user_permission_level(roles, user_permissions)
        
        assert result["is_super_admin"] is False
        assert result["can_access_all"] is False
        assert result["available_permissions"] == ["user:read", "user:create"]
        assert result["role_codes"] == ["user_manager"]

class TestPermissionIntegration:
    """权限集成测试"""
    
    async def test_permission_flow_super_admin(
        self, permission_manager, mock_role_service, super_admin_role
    ):
        """测试超级管理员权限流程"""
        mock_role_service.get_user_roles.return_value = [super_admin_role]
        
        # 获取权限信息
        permission_info = await permission_manager.get_user_permission_info(1)
        assert permission_info["is_super_admin"] is True
        
        # 检查权限
        has_permission = await permission_manager.check_permission(1, "any:permission")
        assert has_permission is True
        
        # 检查多权限
        permissions_check = await permission_manager.check_permissions(1, ["perm1", "perm2"])
        assert all(permissions_check.values())
        
        # 数据访问权限
        data_access = await permission_manager.validate_data_access(1, 999, 888)
        assert data_access is True
    
    async def test_permission_flow_normal_user(
        self, permission_manager, mock_role_service, normal_role, user_permissions
    ):
        """测试普通用户权限流程"""
        mock_role_service.get_user_roles.return_value = [normal_role]
        mock_role_service.get_role_permissions.return_value = user_permissions
        
        # 获取权限信息
        permission_info = await permission_manager.get_user_permission_info(1)
        assert permission_info["is_super_admin"] is False
        
        # 检查有权限的功能
        has_permission = await permission_manager.check_permission(1, "user:read")
        assert has_permission is True
        
        # 检查无权限的功能
        no_permission = await permission_manager.check_permission(1, "admin:all")
        assert no_permission is False
        
        # 数据访问权限 - 自己的资源
        own_data_access = await permission_manager.validate_data_access(1, 1, 100)
        assert own_data_access is True
        
        # 数据访问权限 - 其他资源
        other_data_access = await permission_manager.validate_data_access(1, 999, 888)
        assert other_data_access is False
