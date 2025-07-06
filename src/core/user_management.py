"""
User Management System for News Feed Pro
Handles user authentication, authorization, and user-specific data management
"""

import json
import hashlib
import secrets
import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import os

class UserRole(Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    USER = "user"

class UserStatus(Enum):
    """User account status"""
    PENDING = "pending"      # Registered but not approved
    APPROVED = "approved"    # Approved by admin
    ACTIVE = "active"        # Active and can use the system
    INACTIVE = "inactive"    # Deactivated by admin
    REJECTED = "rejected"    # Rejected by admin

class User:
    """User model for authentication and authorization"""
    
    def __init__(self, user_id: str, username: str, email: str, password_hash: str,
                 role: UserRole = UserRole.USER, status: UserStatus = UserStatus.PENDING,
                 created_at: str = None, approved_at: str = None, approved_by: str = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.datetime.now().isoformat()
        self.approved_at = approved_at
        self.approved_by = approved_by
        self.last_login = None
        self.login_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON storage"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role.value,
            'status': self.status.value,
            'created_at': self.created_at,
            'approved_at': self.approved_at,
            'approved_by': self.approved_by,
            'last_login': self.last_login,
            'login_count': self.login_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        user = cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=UserRole(data['role']),
            status=UserStatus(data['status']),
            created_at=data.get('created_at'),
            approved_at=data.get('approved_at'),
            approved_by=data.get('approved_by')
        )
        user.last_login = data.get('last_login')
        user.login_count = data.get('login_count', 0)
        return user
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches user's password"""
        return self.password_hash == self._hash_password(password)
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = "newsfeeds_salt_2024"  # In production, use random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def is_active(self) -> bool:
        """Check if user is active and can use the system"""
        return self.status == UserStatus.ACTIVE
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role == UserRole.ADMIN

class UserNewsSource:
    """User-specific news source model"""
    
    def __init__(self, source_id: str, user_id: str, name: str, url: str, 
                 category: str = "general", enabled: bool = True, created_at: str = None):
        self.source_id = source_id
        self.user_id = user_id
        self.name = name
        self.url = url
        self.category = category
        self.enabled = enabled
        self.created_at = created_at or datetime.datetime.now().isoformat()
        self.last_fetched = None
        self.fetch_count = 0
        self.error_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert news source to dictionary"""
        return {
            'source_id': self.source_id,
            'user_id': self.user_id,
            'name': self.name,
            'url': self.url,
            'category': self.category,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'last_fetched': self.last_fetched,
            'fetch_count': self.fetch_count,
            'error_count': self.error_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserNewsSource':
        """Create news source from dictionary"""
        source = cls(
            source_id=data['source_id'],
            user_id=data['user_id'],
            name=data['name'],
            url=data['url'],
            category=data.get('category', 'general'),
            enabled=data.get('enabled', True),
            created_at=data.get('created_at')
        )
        source.last_fetched = data.get('last_fetched')
        source.fetch_count = data.get('fetch_count', 0)
        source.error_count = data.get('error_count', 0)
        return source

class UserManager:
    """Manages user data and operations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.user_sources_file = os.path.join(data_dir, "user_sources.json")
        self.audit_log_file = os.path.join(data_dir, "audit_log.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
        
        # Create default admin user if no users exist
        self._create_default_admin()
    
    def _initialize_data_files(self):
        """Initialize JSON data files if they don't exist"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.user_sources_file):
            with open(self.user_sources_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.audit_log_file):
            with open(self.audit_log_file, 'w') as f:
                json.dump([], f)
    
    def _create_default_admin(self):
        """Create default admin user if no users exist"""
        users = self._load_users()
        if not users:
            admin_id = self._generate_user_id()
            admin_user = User(
                user_id=admin_id,
                username="admin",
                email="admin@newsfeeds.local",
                password_hash=User._hash_password("admin123"),  # Default password
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                approved_at=datetime.datetime.now().isoformat(),
                approved_by="system"
            )
            users[admin_id] = admin_user.to_dict()
            self._save_users(users)
            print("✅ Default admin user created: username='admin', password='admin123'")
    
    def _load_users(self) -> Dict[str, Dict]:
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users(self, users: Dict[str, Dict]):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _load_user_sources(self) -> Dict[str, Dict]:
        """Load user sources from JSON file"""
        try:
            with open(self.user_sources_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_user_sources(self, sources: Dict[str, Dict]):
        """Save user sources to JSON file"""
        with open(self.user_sources_file, 'w') as f:
            json.dump(sources, f, indent=2)
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{secrets.token_hex(8)}"
    
    def _generate_source_id(self) -> str:
        """Generate unique source ID"""
        return f"source_{secrets.token_hex(8)}"
    
    def log_audit_event(self, action: str, user_id: str, target_user_id: str = None, details: Dict = None):
        """Log audit event for admin actions"""
        try:
            with open(self.audit_log_file, 'r') as f:
                audit_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            audit_log = []
        
        event = {
            'timestamp': datetime.datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'target_user_id': target_user_id,
            'details': details or {}
        }
        
        audit_log.append(event)
        
        # Keep only last 1000 events
        if len(audit_log) > 1000:
            audit_log = audit_log[-1000:]
        
        with open(self.audit_log_file, 'w') as f:
            json.dump(audit_log, f, indent=2)
    
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user (pending approval)"""
        users = self._load_users()
        
        # Check if username or email already exists
        for user_data in users.values():
            if user_data['username'] == username:
                return {'success': False, 'error': 'Username already exists'}
            if user_data['email'] == email:
                return {'success': False, 'error': 'Email already exists'}
        
        # Create new user
        user_id = self._generate_user_id()
        new_user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=User._hash_password(password),
            role=UserRole.USER,
            status=UserStatus.PENDING
        )
        
        users[user_id] = new_user.to_dict()
        self._save_users(users)
        
        self.log_audit_event("user_registered", user_id, details={'username': username, 'email': email})
        
        return {'success': True, 'user_id': user_id, 'message': 'Registration successful. Awaiting admin approval.'}

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        users = self._load_users()

        for user_data in users.values():
            if user_data['username'] == username:
                user = User.from_dict(user_data)
                if user.check_password(password):
                    if user.is_active():
                        # Update login info
                        user.last_login = datetime.datetime.now().isoformat()
                        user.login_count += 1
                        users[user.user_id] = user.to_dict()
                        self._save_users(users)

                        self.log_audit_event("user_login", user.user_id)
                        return user
                    else:
                        return None  # User not active
                break
        return None  # Invalid credentials

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        users = self._load_users()
        if user_id in users:
            return User.from_dict(users[user_id])
        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        users = self._load_users()
        for user_data in users.values():
            if user_data['username'] == username:
                return User.from_dict(user_data)
        return None

    def get_all_users(self) -> List[User]:
        """Get all users"""
        users = self._load_users()
        return [User.from_dict(user_data) for user_data in users.values()]

    def get_pending_users(self) -> List[User]:
        """Get users pending approval"""
        users = self._load_users()
        return [User.from_dict(user_data) for user_data in users.values()
                if user_data['status'] == UserStatus.PENDING.value]

    def approve_user(self, user_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Approve a pending user"""
        users = self._load_users()

        if user_id not in users:
            return {'success': False, 'error': 'User not found'}

        user_data = users[user_id]
        if user_data['status'] != UserStatus.PENDING.value:
            return {'success': False, 'error': 'User is not pending approval'}

        # Update user status
        user_data['status'] = UserStatus.ACTIVE.value
        user_data['approved_at'] = datetime.datetime.now().isoformat()
        user_data['approved_by'] = admin_user_id

        users[user_id] = user_data
        self._save_users(users)

        self.log_audit_event("user_approved", admin_user_id, user_id,
                           {'username': user_data['username']})

        return {'success': True, 'message': 'User approved successfully'}

    def reject_user(self, user_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Reject a pending user"""
        users = self._load_users()

        if user_id not in users:
            return {'success': False, 'error': 'User not found'}

        user_data = users[user_id]
        if user_data['status'] != UserStatus.PENDING.value:
            return {'success': False, 'error': 'User is not pending approval'}

        # Update user status
        user_data['status'] = UserStatus.REJECTED.value

        users[user_id] = user_data
        self._save_users(users)

        self.log_audit_event("user_rejected", admin_user_id, user_id,
                           {'username': user_data['username']})

        return {'success': True, 'message': 'User rejected successfully'}

    def deactivate_user(self, user_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Deactivate an active user"""
        users = self._load_users()

        if user_id not in users:
            return {'success': False, 'error': 'User not found'}

        user_data = users[user_id]
        if user_data['role'] == UserRole.ADMIN.value:
            return {'success': False, 'error': 'Cannot deactivate admin user'}

        user_data['status'] = UserStatus.INACTIVE.value
        users[user_id] = user_data
        self._save_users(users)

        self.log_audit_event("user_deactivated", admin_user_id, user_id,
                           {'username': user_data['username']})

        return {'success': True, 'message': 'User deactivated successfully'}

    def activate_user(self, user_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Activate an inactive user"""
        users = self._load_users()

        if user_id not in users:
            return {'success': False, 'error': 'User not found'}

        user_data = users[user_id]
        user_data['status'] = UserStatus.ACTIVE.value
        users[user_id] = user_data
        self._save_users(users)

        self.log_audit_event("user_activated", admin_user_id, user_id,
                           {'username': user_data['username']})

        return {'success': True, 'message': 'User activated successfully'}

    def delete_user(self, user_id: str, admin_user_id: str) -> Dict[str, Any]:
        """Delete a user and all their data"""
        users = self._load_users()

        if user_id not in users:
            return {'success': False, 'error': 'User not found'}

        user_data = users[user_id]
        if user_data['role'] == UserRole.ADMIN.value:
            return {'success': False, 'error': 'Cannot delete admin user'}

        # Delete user's news sources
        self.delete_all_user_sources(user_id)

        # Delete user
        username = user_data['username']
        del users[user_id]
        self._save_users(users)

        self.log_audit_event("user_deleted", admin_user_id, user_id,
                           {'username': username})

        return {'success': True, 'message': 'User deleted successfully'}

    # User News Source Preference Management Methods (New Architecture)

    def get_user_source_preferences(self, user_id: str) -> List[str]:
        """Get user's preferred news sources (from global sources)"""
        try:
            prefs_file = os.path.join(self.data_dir, 'user_preferences.json')
            if not os.path.exists(prefs_file):
                return []

            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)

            return prefs.get(user_id, {}).get('enabled_sources', [])
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            return []

    def add_user_source_preference(self, user_id: str, source_name: str) -> Dict[str, Any]:
        """Add a news source preference for a user (max 3 sources)"""
        try:
            # Validate user exists and is active
            user = self.get_user_by_id(user_id)
            if not user or not user.is_active():
                return {'success': False, 'error': 'User not found or not active'}

            # Get current preferences
            current_sources = self.get_user_source_preferences(user_id)

            # Check limit
            if len(current_sources) >= 3:
                return {'success': False, 'error': 'Maximum 3 news sources allowed per user'}

            # Check if already added
            if source_name in current_sources:
                return {'success': False, 'error': 'News source already in your preferences'}

            # Load preferences file
            prefs_file = os.path.join(self.data_dir, 'user_preferences.json')
            prefs = {}
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)

            # Initialize user preferences if not exists
            if user_id not in prefs:
                prefs[user_id] = {'enabled_sources': []}

            # Add source preference
            prefs[user_id]['enabled_sources'].append(source_name)

            # Save preferences
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)

            # Log action
            self.log_audit_event("source_preference_added", user_id,
                               details={'source_name': source_name})

            return {'success': True, 'source_name': source_name}

        except Exception as e:
            logger.error(f"Error adding user source preference: {e}")
            return {'success': False, 'error': 'Failed to add news source preference'}

    def remove_user_source_preference(self, user_id: str, source_name: str) -> Dict[str, Any]:
        """Remove a news source preference for a user"""
        try:
            # Load preferences file
            prefs_file = os.path.join(self.data_dir, 'user_preferences.json')
            if not os.path.exists(prefs_file):
                return {'success': False, 'error': 'No preferences found'}

            with open(prefs_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)

            if user_id not in prefs or source_name not in prefs[user_id].get('enabled_sources', []):
                return {'success': False, 'error': 'Source preference not found'}

            # Remove source preference
            prefs[user_id]['enabled_sources'].remove(source_name)

            # Save preferences
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)

            # Log action
            self.log_audit_event("source_preference_removed", user_id,
                               details={'source_name': source_name})

            return {'success': True, 'source_name': source_name}

        except Exception as e:
            logger.error(f"Error removing user source preference: {e}")
            return {'success': False, 'error': 'Failed to remove news source preference'}

    # Legacy User News Source Management Methods (Keep for compatibility)

    def add_user_source(self, user_id: str, name: str, url: str, category: str = "general") -> Dict[str, Any]:
        """Add a news source for a specific user"""
        # Validate user exists and is active
        user = self.get_user_by_id(user_id)
        if not user or not user.is_active():
            return {'success': False, 'error': 'User not found or not active'}

        sources = self._load_user_sources()

        # Check if user already has a source with this URL
        for source_data in sources.values():
            if source_data['user_id'] == user_id and source_data['url'] == url:
                return {'success': False, 'error': 'Source URL already exists for this user'}

        # Create new source
        source_id = self._generate_source_id()
        new_source = UserNewsSource(
            source_id=source_id,
            user_id=user_id,
            name=name,
            url=url,
            category=category
        )

        sources[source_id] = new_source.to_dict()
        self._save_user_sources(sources)

        self.log_audit_event("source_added", user_id, details={'source_name': name, 'url': url})

        return {'success': True, 'source_id': source_id, 'message': 'News source added successfully'}

    def get_user_sources(self, user_id: str) -> List[UserNewsSource]:
        """Get all news sources for a specific user"""
        sources = self._load_user_sources()
        user_sources = []

        for source_data in sources.values():
            if source_data['user_id'] == user_id:
                user_sources.append(UserNewsSource.from_dict(source_data))

        return user_sources

    def get_user_source_by_id(self, user_id: str, source_id: str) -> Optional[UserNewsSource]:
        """Get a specific news source for a user"""
        sources = self._load_user_sources()

        if source_id in sources:
            source_data = sources[source_id]
            if source_data['user_id'] == user_id:
                return UserNewsSource.from_dict(source_data)

        return None

    def update_user_source(self, user_id: str, source_id: str, name: str = None,
                          url: str = None, category: str = None, enabled: bool = None) -> Dict[str, Any]:
        """Update a user's news source"""
        sources = self._load_user_sources()

        if source_id not in sources:
            return {'success': False, 'error': 'Source not found'}

        source_data = sources[source_id]
        if source_data['user_id'] != user_id:
            return {'success': False, 'error': 'Access denied'}

        # Update fields if provided
        if name is not None:
            source_data['name'] = name
        if url is not None:
            # Check if new URL conflicts with existing sources
            for sid, sdata in sources.items():
                if sid != source_id and sdata['user_id'] == user_id and sdata['url'] == url:
                    return {'success': False, 'error': 'Source URL already exists for this user'}
            source_data['url'] = url
        if category is not None:
            source_data['category'] = category
        if enabled is not None:
            source_data['enabled'] = enabled

        sources[source_id] = source_data
        self._save_user_sources(sources)

        self.log_audit_event("source_updated", user_id, details={'source_id': source_id, 'name': source_data['name']})

        return {'success': True, 'message': 'News source updated successfully'}

    def delete_user_source(self, user_id: str, source_id: str) -> Dict[str, Any]:
        """Delete a user's news source"""
        sources = self._load_user_sources()

        if source_id not in sources:
            return {'success': False, 'error': 'Source not found'}

        source_data = sources[source_id]
        if source_data['user_id'] != user_id:
            return {'success': False, 'error': 'Access denied'}

        source_name = source_data['name']
        del sources[source_id]
        self._save_user_sources(sources)

        self.log_audit_event("source_deleted", user_id, details={'source_id': source_id, 'name': source_name})

        return {'success': True, 'message': 'News source deleted successfully'}

    def delete_all_user_sources(self, user_id: str) -> int:
        """Delete all news sources for a user (used when deleting user)"""
        sources = self._load_user_sources()
        deleted_count = 0

        sources_to_delete = [sid for sid, sdata in sources.items() if sdata['user_id'] == user_id]

        for source_id in sources_to_delete:
            del sources[source_id]
            deleted_count += 1

        if deleted_count > 0:
            self._save_user_sources(sources)

        return deleted_count

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get audit log entries"""
        try:
            with open(self.audit_log_file, 'r') as f:
                audit_log = json.load(f)
            return audit_log[-limit:] if limit else audit_log
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_user_stats(self) -> Dict[str, int]:
        """Get user statistics for admin dashboard"""
        users = self._load_users()
        stats = {
            'total_users': len(users),
            'active_users': 0,
            'pending_users': 0,
            'inactive_users': 0,
            'rejected_users': 0,
            'admin_users': 0
        }

        for user_data in users.values():
            status = user_data['status']
            role = user_data['role']

            if status == UserStatus.ACTIVE.value:
                stats['active_users'] += 1
            elif status == UserStatus.PENDING.value:
                stats['pending_users'] += 1
            elif status == UserStatus.INACTIVE.value:
                stats['inactive_users'] += 1
            elif status == UserStatus.REJECTED.value:
                stats['rejected_users'] += 1

            if role == UserRole.ADMIN.value:
                stats['admin_users'] += 1

        return stats
