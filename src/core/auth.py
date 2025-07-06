"""
Authentication and Authorization System for News Feed Pro
Handles session management, login/logout, and role-based access control
"""

import functools
import secrets
import datetime
from typing import Dict, Optional, Any
from flask import session, request, jsonify, redirect, url_for, g
from .user_management import UserManager, User, UserRole, UserStatus

class SessionManager:
    """Manages user sessions and authentication"""
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        self.active_sessions = {}  # In production, use Redis or database
    
    def create_session(self, user: User) -> str:
        """Create a new session for authenticated user"""
        session_token = secrets.token_hex(32)
        session_data = {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role.value,
            'created_at': datetime.datetime.now().isoformat(),
            'last_activity': datetime.datetime.now().isoformat()
        }
        
        self.active_sessions[session_token] = session_data
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session data by token"""
        if session_token in self.active_sessions:
            session_data = self.active_sessions[session_token]
            # Update last activity
            session_data['last_activity'] = datetime.datetime.now().isoformat()
            return session_data
        return None
    
    def destroy_session(self, session_token: str) -> bool:
        """Destroy a session"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Clean up expired sessions"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=max_age_hours)
        expired_tokens = []
        
        for token, session_data in self.active_sessions.items():
            last_activity = datetime.datetime.fromisoformat(session_data['last_activity'])
            if last_activity < cutoff_time:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self.active_sessions[token]
        
        return len(expired_tokens)

class AuthManager:
    """Main authentication manager"""
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        self.session_manager = SessionManager(user_manager)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session"""
        user = self.user_manager.authenticate_user(username, password)
        
        if not user:
            return {'success': False, 'error': 'Invalid username or password'}
        
        if not user.is_active():
            if user.status == UserStatus.PENDING:
                return {'success': False, 'error': 'Account pending admin approval'}
            elif user.status == UserStatus.INACTIVE:
                return {'success': False, 'error': 'Account has been deactivated'}
            elif user.status == UserStatus.REJECTED:
                return {'success': False, 'error': 'Account registration was rejected'}
            else:
                return {'success': False, 'error': 'Account is not active'}
        
        # Create session
        session_token = self.session_manager.create_session(user)
        
        return {
            'success': True,
            'session_token': session_token,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'status': user.status.value
            }
        }
    
    def logout(self, session_token: str) -> Dict[str, Any]:
        """Logout user and destroy session"""
        if self.session_manager.destroy_session(session_token):
            return {'success': True, 'message': 'Logged out successfully'}
        return {'success': False, 'error': 'Invalid session'}
    
    def get_current_user(self, session_token: str) -> Optional[User]:
        """Get current user from session token"""
        session_data = self.session_manager.get_session(session_token)
        if session_data:
            return self.user_manager.get_user_by_id(session_data['user_id'])
        return None
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        return self.user_manager.register_user(username, email, password)

# Global auth manager instance (will be initialized in main app)
auth_manager = None

def init_auth(user_manager: UserManager):
    """Initialize authentication system"""
    global auth_manager
    auth_manager = AuthManager(user_manager)
    return auth_manager

def get_current_user() -> Optional[User]:
    """Get current user from Flask session or request headers"""
    if not auth_manager:
        return None
    
    # Try to get session token from Flask session
    session_token = session.get('session_token')
    
    # If not in session, try Authorization header
    if not session_token:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    if session_token:
        return auth_manager.get_current_user(session_token)
    
    return None

def login_required(f):
    """Decorator to require user login"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        # Store user in Flask g for easy access
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        if not user.is_admin():
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            return jsonify({'error': 'Access denied'}), 403
        
        # Store user in Flask g for easy access
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(required_role: UserRole):
    """Decorator to require specific role"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('login'))
            
            if user.role != required_role:
                if request.is_json:
                    return jsonify({'error': f'{required_role.value} access required'}), 403
                return jsonify({'error': 'Access denied'}), 403
            
            # Store user in Flask g for easy access
            g.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def user_owns_resource(resource_user_id_param: str = 'user_id'):
    """Decorator to ensure user can only access their own resources"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('login'))
            
            # Admin can access any resource
            if user.is_admin():
                g.current_user = user
                return f(*args, **kwargs)
            
            # Get resource user ID from request
            resource_user_id = None
            
            # Try to get from URL parameters
            if resource_user_id_param in kwargs:
                resource_user_id = kwargs[resource_user_id_param]
            # Try to get from request JSON
            elif request.is_json and resource_user_id_param in request.json:
                resource_user_id = request.json[resource_user_id_param]
            # Try to get from form data
            elif resource_user_id_param in request.form:
                resource_user_id = request.form[resource_user_id_param]
            # Try to get from query parameters
            elif resource_user_id_param in request.args:
                resource_user_id = request.args[resource_user_id_param]
            
            # Check if user owns the resource
            if resource_user_id != user.user_id:
                if request.is_json:
                    return jsonify({'error': 'Access denied'}), 403
                return jsonify({'error': 'Access denied'}), 403
            
            # Store user in Flask g for easy access
            g.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def optional_auth(f):
    """Decorator for optional authentication (user may or may not be logged in)"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        g.current_user = user  # May be None
        return f(*args, **kwargs)
    
    return decorated_function
