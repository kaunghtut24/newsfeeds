"""
Admin Settings Management System
Handles configurable limits and system-wide settings
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class UserLimits:
    """User limits configuration"""
    max_sources_per_user: int = 6  # Total: 3 global + 3 custom
    max_articles_per_source: int = 20
    fetch_interval_minutes: int = 30
    max_fetch_requests_per_hour: int = 10
    max_custom_sources_per_user: int = 3  # User can add 3 custom sources
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserLimits':
        return cls(**data)

@dataclass
class SystemSettings:
    """System-wide settings"""
    auto_add_user_sources_to_global: bool = True
    require_admin_approval_for_custom_sources: bool = False  # Allow auto-add without approval
    enable_user_fetch_scheduling: bool = True
    default_fetch_interval_minutes: int = 30
    max_global_sources: int = 50
    enable_source_quality_scoring: bool = True
    default_user_source: str = "BBC News"  # Default source for new users
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemSettings':
        return cls(**data)

class AdminSettingsManager:
    """Manages admin-configurable settings and user limits"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.settings_file = os.path.join(data_dir, 'admin_settings.json')
        self.user_limits = UserLimits()
        self.system_settings = SystemSettings()
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'user_limits' in data:
                    self.user_limits = UserLimits.from_dict(data['user_limits'])
                
                if 'system_settings' in data:
                    self.system_settings = SystemSettings.from_dict(data['system_settings'])
                    
                logger.info("Admin settings loaded successfully")
            else:
                # Create default settings file
                self._save_settings()
                logger.info("Created default admin settings")
                
        except Exception as e:
            logger.error(f"Error loading admin settings: {e}")
            # Use defaults
            self.user_limits = UserLimits()
            self.system_settings = SystemSettings()
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            settings_data = {
                'user_limits': self.user_limits.to_dict(),
                'system_settings': self.system_settings.to_dict(),
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
                
            logger.info("Admin settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving admin settings: {e}")
    
    def get_user_limits(self) -> UserLimits:
        """Get current user limits"""
        return self.user_limits
    
    def get_system_settings(self) -> SystemSettings:
        """Get current system settings"""
        return self.system_settings
    
    def update_user_limits(self, **kwargs) -> Dict[str, Any]:
        """Update user limits"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.user_limits, key):
                    setattr(self.user_limits, key, value)
                else:
                    return {'success': False, 'error': f'Invalid setting: {key}'}
            
            self._save_settings()
            return {'success': True, 'user_limits': self.user_limits.to_dict()}
            
        except Exception as e:
            logger.error(f"Error updating user limits: {e}")
            return {'success': False, 'error': 'Failed to update user limits'}
    
    def update_system_settings(self, **kwargs) -> Dict[str, Any]:
        """Update system settings"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.system_settings, key):
                    setattr(self.system_settings, key, value)
                else:
                    return {'success': False, 'error': f'Invalid setting: {key}'}
            
            self._save_settings()
            return {'success': True, 'system_settings': self.system_settings.to_dict()}
            
        except Exception as e:
            logger.error(f"Error updating system settings: {e}")
            return {'success': False, 'error': 'Failed to update system settings'}
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return {
            'user_limits': self.user_limits.to_dict(),
            'system_settings': self.system_settings.to_dict(),
            'last_updated': datetime.now().isoformat()
        }
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """Reset all settings to defaults"""
        try:
            self.user_limits = UserLimits()
            self.system_settings = SystemSettings()
            self._save_settings()
            
            return {'success': True, 'message': 'Settings reset to defaults'}
            
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return {'success': False, 'error': 'Failed to reset settings'}
    
    def validate_user_action(self, user_id: str, action: str, **params) -> Dict[str, Any]:
        """Validate if user can perform an action based on current limits"""
        try:
            if action == 'add_source':
                current_count = params.get('current_source_count', 0)
                max_allowed = self.user_limits.max_sources_per_user
                
                if current_count >= max_allowed:
                    return {
                        'allowed': False, 
                        'reason': f'Maximum {max_allowed} sources allowed per user'
                    }
            
            elif action == 'add_custom_source':
                current_custom_count = params.get('current_custom_count', 0)
                max_custom = self.user_limits.max_custom_sources_per_user
                
                if current_custom_count >= max_custom:
                    return {
                        'allowed': False,
                        'reason': f'Maximum {max_custom} custom sources allowed per user'
                    }
            
            elif action == 'fetch_news':
                # Check fetch frequency limits
                last_fetch = params.get('last_fetch_time')
                if last_fetch:
                    from datetime import datetime, timedelta
                    time_since_last = datetime.now() - last_fetch
                    min_interval = timedelta(minutes=self.user_limits.fetch_interval_minutes)
                    
                    if time_since_last < min_interval:
                        remaining = min_interval - time_since_last
                        return {
                            'allowed': False,
                            'reason': f'Please wait {remaining.seconds // 60} more minutes before fetching again'
                        }
            
            return {'allowed': True}
            
        except Exception as e:
            logger.error(f"Error validating user action: {e}")
            return {'allowed': False, 'reason': 'Validation error'}
