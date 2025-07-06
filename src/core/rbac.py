"""
Role-Based Access Control (RBAC) System for News Feed Pro
Defines permissions, roles, and access control policies
"""

from enum import Enum
from typing import Dict, List, Set, Any
from .user_management import UserRole, User

class Permission(Enum):
    """System permissions"""
    # User management permissions
    VIEW_USERS = "view_users"
    APPROVE_USERS = "approve_users"
    DEACTIVATE_USERS = "deactivate_users"
    DELETE_USERS = "delete_users"
    
    # News source permissions
    MANAGE_OWN_SOURCES = "manage_own_sources"
    VIEW_ALL_SOURCES = "view_all_sources"
    MANAGE_ALL_SOURCES = "manage_all_sources"
    
    # AI features permissions
    USE_AI_FEATURES = "use_ai_features"
    CONFIGURE_AI_SETTINGS = "configure_ai_settings"
    
    # System permissions
    VIEW_ADMIN_DASHBOARD = "view_admin_dashboard"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"
    
    # Content permissions
    VIEW_OWN_CONTENT = "view_own_content"
    VIEW_ALL_CONTENT = "view_all_content"
    GENERATE_REPORTS = "generate_reports"

class RolePermissions:
    """Defines permissions for each role"""
    
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: {
            # User management
            Permission.VIEW_USERS,
            Permission.APPROVE_USERS,
            Permission.DEACTIVATE_USERS,
            Permission.DELETE_USERS,
            
            # News sources
            Permission.MANAGE_OWN_SOURCES,
            Permission.VIEW_ALL_SOURCES,
            Permission.MANAGE_ALL_SOURCES,
            
            # AI features
            Permission.USE_AI_FEATURES,
            Permission.CONFIGURE_AI_SETTINGS,
            
            # System
            Permission.VIEW_ADMIN_DASHBOARD,
            Permission.VIEW_AUDIT_LOGS,
            Permission.MANAGE_SYSTEM_SETTINGS,
            
            # Content
            Permission.VIEW_OWN_CONTENT,
            Permission.VIEW_ALL_CONTENT,
            Permission.GENERATE_REPORTS,
        },
        
        UserRole.USER: {
            # News sources
            Permission.MANAGE_OWN_SOURCES,
            
            # AI features
            Permission.USE_AI_FEATURES,
            
            # Content
            Permission.VIEW_OWN_CONTENT,
            Permission.GENERATE_REPORTS,
        }
    }
    
    @classmethod
    def get_permissions(cls, role: UserRole) -> Set[Permission]:
        """Get permissions for a role"""
        return cls.ROLE_PERMISSIONS.get(role, set())
    
    @classmethod
    def has_permission(cls, role: UserRole, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in cls.get_permissions(role)

class AccessControl:
    """Access control utilities"""
    
    @staticmethod
    def check_permission(user: User, permission: Permission) -> bool:
        """Check if user has specific permission"""
        if not user or not user.is_active():
            return False
        
        return RolePermissions.has_permission(user.role, permission)
    
    @staticmethod
    def check_multiple_permissions(user: User, permissions: List[Permission], require_all: bool = True) -> bool:
        """Check if user has multiple permissions"""
        if not user or not user.is_active():
            return False
        
        user_permissions = RolePermissions.get_permissions(user.role)
        
        if require_all:
            return all(perm in user_permissions for perm in permissions)
        else:
            return any(perm in user_permissions for perm in permissions)
    
    @staticmethod
    def can_manage_user(current_user: User, target_user: User) -> bool:
        """Check if current user can manage target user"""
        if not current_user or not current_user.is_active():
            return False
        
        # Users cannot manage themselves for critical operations
        if current_user.user_id == target_user.user_id:
            return False
        
        # Only admins can manage users
        if not current_user.is_admin():
            return False
        
        # Admins cannot manage other admins (prevent admin lockout)
        if target_user.is_admin():
            return False
        
        return True
    
    @staticmethod
    def can_access_user_data(current_user: User, target_user_id: str) -> bool:
        """Check if current user can access target user's data"""
        if not current_user or not current_user.is_active():
            return False
        
        # Users can access their own data
        if current_user.user_id == target_user_id:
            return True
        
        # Admins can access any user's data
        if current_user.is_admin():
            return True
        
        return False
    
    @staticmethod
    def can_manage_news_source(current_user: User, source_user_id: str) -> bool:
        """Check if current user can manage a news source"""
        if not current_user or not current_user.is_active():
            return False
        
        # Users can manage their own sources
        if current_user.user_id == source_user_id:
            return AccessControl.check_permission(current_user, Permission.MANAGE_OWN_SOURCES)
        
        # Admins can manage any sources
        if current_user.is_admin():
            return AccessControl.check_permission(current_user, Permission.MANAGE_ALL_SOURCES)
        
        return False
    
    @staticmethod
    def get_accessible_user_ids(current_user: User, all_user_ids: List[str]) -> List[str]:
        """Get list of user IDs that current user can access"""
        if not current_user or not current_user.is_active():
            return []
        
        # Admins can access all users
        if current_user.is_admin():
            return all_user_ids
        
        # Regular users can only access their own data
        return [current_user.user_id] if current_user.user_id in all_user_ids else []

class PermissionChecker:
    """Utility class for checking permissions in templates and views"""
    
    def __init__(self, user: User):
        self.user = user
    
    def can(self, permission: Permission) -> bool:
        """Check if user has permission"""
        return AccessControl.check_permission(self.user, permission)
    
    def can_any(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the permissions"""
        return AccessControl.check_multiple_permissions(self.user, permissions, require_all=False)
    
    def can_all(self, permissions: List[Permission]) -> bool:
        """Check if user has all permissions"""
        return AccessControl.check_multiple_permissions(self.user, permissions, require_all=True)
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.user and self.user.is_admin()
    
    def is_user(self) -> bool:
        """Check if user is regular user"""
        return self.user and self.user.role == UserRole.USER
    
    def can_manage_user(self, target_user: User) -> bool:
        """Check if can manage target user"""
        return AccessControl.can_manage_user(self.user, target_user)
    
    def can_access_user_data(self, target_user_id: str) -> bool:
        """Check if can access target user's data"""
        return AccessControl.can_access_user_data(self.user, target_user_id)
    
    def can_manage_source(self, source_user_id: str) -> bool:
        """Check if can manage news source"""
        return AccessControl.can_manage_news_source(self.user, source_user_id)

def get_permission_checker(user: User) -> PermissionChecker:
    """Get permission checker for user"""
    return PermissionChecker(user)

# Permission groups for easier management
ADMIN_PERMISSIONS = RolePermissions.get_permissions(UserRole.ADMIN)
USER_PERMISSIONS = RolePermissions.get_permissions(UserRole.USER)

# Common permission sets
USER_MANAGEMENT_PERMISSIONS = [
    Permission.VIEW_USERS,
    Permission.APPROVE_USERS,
    Permission.DEACTIVATE_USERS,
    Permission.DELETE_USERS
]

CONTENT_MANAGEMENT_PERMISSIONS = [
    Permission.VIEW_ALL_CONTENT,
    Permission.MANAGE_ALL_SOURCES,
    Permission.GENERATE_REPORTS
]

SYSTEM_ADMIN_PERMISSIONS = [
    Permission.VIEW_ADMIN_DASHBOARD,
    Permission.VIEW_AUDIT_LOGS,
    Permission.MANAGE_SYSTEM_SETTINGS,
    Permission.CONFIGURE_AI_SETTINGS
]
