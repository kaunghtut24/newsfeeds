"""
Enhanced User Source Management System
Supports both global sources and user-added custom sources
"""

import json
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Import source validator
try:
    from .source_validator import SourceValidator, SourceValidationResult
except ImportError:
    # Fallback if validator not available
    SourceValidator = None
    SourceValidationResult = None

# Import global news sources configuration
import json
import os

def load_news_sources():
    """Load news sources from config.json"""
    try:
        config_path = os.path.join(os.getcwd(), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('news_sources', {})
    except Exception as e:
        logger.error(f"Error loading news sources: {e}")
    return {}

# Load news sources from config
news_sources = load_news_sources()

logger = logging.getLogger(__name__)

class SourceType(Enum):
    GLOBAL = "global"
    USER_CUSTOM = "user_custom"
    USER_APPROVED = "user_approved"  # User-added but admin-approved

class SourceStatus(Enum):
    ACTIVE = "active"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISABLED = "disabled"

class SourceTag(Enum):
    DEFAULT = "default"  # Pre-added for all users
    OPTIONAL = "optional"  # Users can opt-in
    PREMIUM = "premium"  # Special sources
    EXPERIMENTAL = "experimental"  # Beta sources

@dataclass
class UserSource:
    """Enhanced user source with custom source support"""
    source_id: str
    user_id: str
    name: str
    url: str
    category: str = "general"
    source_type: SourceType = SourceType.GLOBAL
    status: SourceStatus = SourceStatus.ACTIVE
    enabled: bool = True
    created_at: str = None
    last_fetched: str = None
    fetch_count: int = 0
    error_count: int = 0
    max_articles: int = 20
    fetch_interval_minutes: int = 30
    quality_score: float = 0.0
    user_notes: str = ""
    # New fields for enhanced workflow
    tags: List[str] = None  # Source tags (default, optional, etc.)
    validation_result: Dict[str, Any] = None  # Validation test results
    rejection_reason: str = ""  # Reason for rejection
    reviewed_by: str = ""  # Admin who reviewed
    reviewed_at: str = ""  # When reviewed
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['source_type'] = self.source_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSource':
        # Convert enum strings back to enums
        if 'source_type' in data:
            data['source_type'] = SourceType(data['source_type'])
        if 'status' in data:
            data['status'] = SourceStatus(data['status'])
        return cls(**data)
    
    def can_fetch_now(self) -> bool:
        """Check if enough time has passed since last fetch"""
        if not self.last_fetched:
            return True
        
        last_fetch = datetime.fromisoformat(self.last_fetched)
        time_since = datetime.now() - last_fetch
        return time_since >= timedelta(minutes=self.fetch_interval_minutes)
    
    def update_fetch_stats(self, success: bool = True):
        """Update fetch statistics"""
        self.last_fetched = datetime.now().isoformat()
        self.fetch_count += 1
        if not success:
            self.error_count += 1

@dataclass
class UserFetchSchedule:
    """User's personalized fetch schedule"""
    user_id: str
    enabled: bool = True
    fetch_interval_minutes: int = 30
    max_articles_per_source: int = 20
    auto_fetch: bool = True
    fetch_hours_start: int = 6  # 6 AM
    fetch_hours_end: int = 22   # 10 PM
    last_fetch_time: str = None
    fetch_count_today: int = 0
    max_fetches_per_day: int = 48  # Every 30 minutes = 48 times per day
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserFetchSchedule':
        return cls(**data)
    
    def can_fetch_now(self) -> bool:
        """Check if user can fetch now based on schedule"""
        current_hour = datetime.now().hour
        
        # Check if within allowed hours
        if not (self.fetch_hours_start <= current_hour <= self.fetch_hours_end):
            return False
        
        # Check daily limit
        if self.fetch_count_today >= self.max_fetches_per_day:
            return False
        
        # Check interval
        if self.last_fetch_time:
            last_fetch = datetime.fromisoformat(self.last_fetch_time)
            time_since = datetime.now() - last_fetch
            if time_since < timedelta(minutes=self.fetch_interval_minutes):
                return False
        
        return True

class EnhancedUserSourceManager:
    """Enhanced user source manager with custom sources and admin controls"""
    
    def __init__(self, data_dir: str, admin_settings_manager):
        self.data_dir = data_dir
        self.admin_settings = admin_settings_manager
        self.user_sources_file = os.path.join(data_dir, 'enhanced_user_sources.json')
        self.user_schedules_file = os.path.join(data_dir, 'user_fetch_schedules.json')
        self.global_sources_file = os.path.join(data_dir, 'dynamic_global_sources.json')
        
        self.user_sources = {}  # user_id -> [UserSource]
        self.user_schedules = {}  # user_id -> UserFetchSchedule
        self.global_sources = {}  # source_name -> source_config
        
        self._load_data()
    
    def _load_data(self):
        """Load all user source data"""
        try:
            # Load user sources
            if os.path.exists(self.user_sources_file):
                with open(self.user_sources_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, sources_data in data.items():
                        self.user_sources[user_id] = [
                            UserSource.from_dict(source_data) 
                            for source_data in sources_data
                        ]
            
            # Load user schedules
            if os.path.exists(self.user_schedules_file):
                with open(self.user_schedules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, schedule_data in data.items():
                        self.user_schedules[user_id] = UserFetchSchedule.from_dict(schedule_data)
            
            # Load dynamic global sources
            if os.path.exists(self.global_sources_file):
                with open(self.global_sources_file, 'r', encoding='utf-8') as f:
                    self.global_sources = json.load(f)
            
            logger.info("Enhanced user source data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading enhanced user source data: {e}")
    
    def _save_user_sources(self):
        """Save user sources to file"""
        try:
            data = {}
            for user_id, sources in self.user_sources.items():
                data[user_id] = [source.to_dict() for source in sources]
            
            with open(self.user_sources_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving user sources: {e}")
    
    def _save_user_schedules(self):
        """Save user schedules to file"""
        try:
            data = {}
            for user_id, schedule in self.user_schedules.items():
                data[user_id] = schedule.to_dict()
            
            with open(self.user_schedules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving user schedules: {e}")
    
    def _save_global_sources(self):
        """Save dynamic global sources to file"""
        try:
            with open(self.global_sources_file, 'w', encoding='utf-8') as f:
                json.dump(self.global_sources, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving global sources: {e}")
    
    def get_user_sources(self, user_id: str) -> List[UserSource]:
        """Get all sources for a user"""
        return self.user_sources.get(user_id, [])
    
    def get_user_schedule(self, user_id: str) -> UserFetchSchedule:
        """Get user's fetch schedule"""
        if user_id not in self.user_schedules:
            # Create default schedule with admin settings
            limits = self.admin_settings.get_user_limits()
            self.user_schedules[user_id] = UserFetchSchedule(
                user_id=user_id,
                fetch_interval_minutes=limits.fetch_interval_minutes,
                max_articles_per_source=limits.max_articles_per_source
            )
            self._save_user_schedules()

        return self.user_schedules[user_id]

    def ensure_user_has_default_source(self, user_id: str):
        """Ensure user has the admin-set default source"""
        try:
            user_sources = self.get_user_sources(user_id)

            # If user has no sources, add the default source
            if not user_sources:
                system_settings = self.admin_settings.get_system_settings()
                default_source = system_settings.default_user_source

                # Refresh news sources and check if default source exists
                global news_sources
                news_sources = load_news_sources()

                if default_source in news_sources:
                    source_config = news_sources[default_source]

                    # Handle both string URLs and dict configurations
                    if isinstance(source_config, str):
                        url = source_config
                        category = 'General'
                    else:
                        url = source_config.get('url', '')
                        category = source_config.get('category', 'General')

                    result = self.add_user_source(
                        user_id=user_id,
                        name=default_source,
                        url=url,
                        category=category,
                        source_type=SourceType.GLOBAL
                    )

                    if result['success']:
                        logger.info(f"Added default source '{default_source}' for user {user_id}")
                    else:
                        logger.warning(f"Failed to add default source for user {user_id}: {result.get('error')}")

        except Exception as e:
            logger.error(f"Error ensuring default source for user {user_id}: {e}")

    def get_user_source_preferences(self, user_id: str) -> List[str]:
        """Get list of source names that user has selected"""
        try:
            # Ensure user has default source
            self.ensure_user_has_default_source(user_id)

            user_sources = self.get_user_sources(user_id)
            active_sources = [
                source.name for source in user_sources
                if source.enabled and source.status in [SourceStatus.ACTIVE, SourceStatus.APPROVED]
            ]
            return active_sources

        except Exception as e:
            logger.error(f"Error getting user source preferences: {e}")
            return []

    def add_user_source(self, user_id: str, name: str, url: str, category: str = "general",
                       source_type: SourceType = SourceType.GLOBAL) -> Dict[str, Any]:
        """Add a source for a user (global or custom)"""
        try:
            # Get current user sources
            current_sources = self.get_user_sources(user_id)
            limits = self.admin_settings.get_user_limits()

            # Check for duplicate source names or URLs
            for source in current_sources:
                if source.name == name:
                    return {
                        'success': False,
                        'error': f'News source "{name}" already in your preferences'
                    }
                if source.url == url:
                    return {
                        'success': False,
                        'error': f'A source with this URL already exists in your preferences as "{source.name}"'
                    }

            # Check limits based on source type (3 global + 3 custom = 6 total)
            global_count = len([s for s in current_sources if s.source_type == SourceType.GLOBAL])
            custom_count = len([s for s in current_sources if s.source_type == SourceType.USER_CUSTOM])

            if source_type == SourceType.GLOBAL:
                # Check global source limit (max 3 global sources)
                if global_count >= limits.max_sources_per_user:
                    return {
                        'success': False,
                        'error': f'Maximum {limits.max_sources_per_user} global sources allowed per user'
                    }
            elif source_type == SourceType.USER_CUSTOM:
                # Check custom source limit (max 3 custom sources)
                if custom_count >= limits.max_custom_sources_per_user:
                    return {
                        'success': False,
                        'error': f'Maximum {limits.max_custom_sources_per_user} custom sources allowed per user'
                    }

            # Total limit check (should allow up to 6 total: 3 global + 3 custom)
            total_allowed = limits.max_sources_per_user + limits.max_custom_sources_per_user
            if len(current_sources) >= total_allowed:
                return {
                    'success': False,
                    'error': f'Maximum {total_allowed} total sources allowed per user ({limits.max_sources_per_user} global + {limits.max_custom_sources_per_user} custom)'
                }

            # Create new source
            source_id = f"source_{uuid.uuid4().hex[:16]}"

            # Check if custom sources need approval
            system_settings = self.admin_settings.get_system_settings()
            if source_type == SourceType.USER_CUSTOM and system_settings.require_admin_approval_for_custom_sources:
                status = SourceStatus.PENDING_APPROVAL
            else:
                status = SourceStatus.ACTIVE

            new_source = UserSource(
                source_id=source_id,
                user_id=user_id,
                name=name,
                url=url,
                category=category,
                source_type=source_type,
                status=status,
                max_articles=limits.max_articles_per_source,
                fetch_interval_minutes=limits.fetch_interval_minutes
            )

            # Add to user sources
            if user_id not in self.user_sources:
                self.user_sources[user_id] = []

            self.user_sources[user_id].append(new_source)
            self._save_user_sources()

            # If it's a custom source and auto-add is enabled, add to global sources
            system_settings = self.admin_settings.get_system_settings()
            if (source_type == SourceType.USER_CUSTOM and
                system_settings.auto_add_user_sources_to_global and
                not system_settings.require_admin_approval_for_custom_sources):

                self._add_to_global_sources(name, url, category)

            return {'success': True, 'source': new_source.to_dict()}

        except Exception as e:
            logger.error(f"Error adding user source: {e}")
            return {'success': False, 'error': 'Failed to add source'}

    def remove_user_source(self, user_id: str, source_id: str) -> Dict[str, Any]:
        """Remove a user source"""
        try:
            user_sources = self.get_user_sources(user_id)

            for i, source in enumerate(user_sources):
                if source.source_id == source_id:
                    removed_source = user_sources.pop(i)
                    self.user_sources[user_id] = user_sources
                    self._save_user_sources()

                    return {'success': True, 'removed_source': removed_source.to_dict()}

            return {'success': False, 'error': 'Source not found'}

        except Exception as e:
            logger.error(f"Error removing user source: {e}")
            return {'success': False, 'error': 'Failed to remove source'}

    def update_user_schedule(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Update user's fetch schedule"""
        try:
            schedule = self.get_user_schedule(user_id)

            for key, value in kwargs.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)

            self.user_schedules[user_id] = schedule
            self._save_user_schedules()

            return {'success': True, 'schedule': schedule.to_dict()}

        except Exception as e:
            logger.error(f"Error updating user schedule: {e}")
            return {'success': False, 'error': 'Failed to update schedule'}

    def can_user_fetch_now(self, user_id: str) -> Dict[str, Any]:
        """Check if user can fetch news now"""
        try:
            schedule = self.get_user_schedule(user_id)

            if not schedule.can_fetch_now():
                return {
                    'can_fetch': False,
                    'reason': 'Fetch interval or daily limit reached',
                    'next_fetch_time': self._calculate_next_fetch_time(schedule)
                }

            return {'can_fetch': True}

        except Exception as e:
            logger.error(f"Error checking fetch permission: {e}")
            return {'can_fetch': False, 'reason': 'Error checking permissions'}

    def add_user_source_preference(self, user_id: str, source_name: str) -> Dict[str, Any]:
        """Add a source preference for a user (from global sources only)"""
        try:
            # Refresh news sources to get latest configuration
            global news_sources
            news_sources = load_news_sources()

            # Check if source exists in global sources
            if source_name not in news_sources:
                logger.error(f"Source '{source_name}' not found in news_sources: {list(news_sources.keys())}")
                return {
                    'success': False,
                    'error': f'Source not found in global configuration. Available sources: {list(news_sources.keys())}'
                }

            # Note: Duplicate and limit checks are handled by add_user_source method

            # Get source configuration
            source_config = news_sources[source_name]
            if isinstance(source_config, str):
                url = source_config
                category = 'General'
            else:
                url = source_config.get('url', '')
                category = source_config.get('category', 'General')

            # Add the source
            result = self.add_user_source(
                user_id=user_id,
                name=source_name,
                url=url,
                category=category,
                source_type=SourceType.GLOBAL
            )

            return result

        except Exception as e:
            logger.error(f"Error adding user source preference: {e}")
            return {'success': False, 'error': 'Failed to add source preference'}

    def remove_user_source_preference(self, user_id: str, source_name: str) -> Dict[str, Any]:
        """Remove a source preference for a user"""
        try:
            user_sources = self.get_user_sources(user_id)

            for source in user_sources:
                if source.name == source_name:
                    return self.remove_user_source(user_id, source.source_id)

            return {'success': False, 'error': 'Source not found in your preferences'}

        except Exception as e:
            logger.error(f"Error removing user source preference: {e}")
            return {'success': False, 'error': 'Failed to remove source preference'}

    def toggle_global_source_availability(self, source_name: str, enabled: bool) -> Dict[str, Any]:
        """Toggle global source availability (Admin only)"""
        try:
            # Refresh news sources to ensure we have latest config
            global news_sources
            news_sources = load_news_sources()

            if source_name not in news_sources:
                return {
                    'success': False,
                    'error': f'Source {source_name} not found in global configuration'
                }

            # Load current global source states
            global_states = self._load_global_source_states()

            # Update the state
            global_states[source_name] = enabled

            # Save the updated states
            self._save_global_source_states(global_states)

            logger.info(f"Admin toggled global source '{source_name}' to {'enabled' if enabled else 'disabled'}")

            return {
                'success': True,
                'message': f'Global source {source_name} {"enabled" if enabled else "disabled"} successfully'
            }

        except Exception as e:
            logger.error(f"Error toggling global source availability: {e}")
            return {'success': False, 'error': 'Failed to toggle global source availability'}

    def _load_global_source_states(self) -> Dict[str, bool]:
        """Load global source enabled/disabled states"""
        try:
            states_file = os.path.join(self.data_dir, 'global_source_states.json')
            if os.path.exists(states_file):
                with open(states_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Default: all sources enabled
                global news_sources
                news_sources = load_news_sources()
                return {source_name: True for source_name in news_sources.keys()}
        except Exception as e:
            logger.error(f"Error loading global source states: {e}")
            return {}

    def _save_global_source_states(self, states: Dict[str, bool]) -> None:
        """Save global source enabled/disabled states"""
        try:
            states_file = os.path.join(self.data_dir, 'global_source_states.json')
            with open(states_file, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving global source states: {e}")

    def get_global_source_states(self) -> Dict[str, bool]:
        """Get current global source states"""
        return self._load_global_source_states()

    def _calculate_next_fetch_time(self, schedule: UserFetchSchedule) -> str:
        """Calculate when user can fetch next"""
        if schedule.last_fetch_time:
            last_fetch = datetime.fromisoformat(schedule.last_fetch_time)
            next_fetch = last_fetch + timedelta(minutes=schedule.fetch_interval_minutes)
            return next_fetch.isoformat()
        return datetime.now().isoformat()

    def _add_to_global_sources(self, name: str, url: str, category: str):
        """Add user source to global sources (updates config.json)"""
        try:
            # Add to internal global sources
            self.global_sources[name] = {
                'url': url,
                'category': category,
                'type': 'rss',
                'added_by_user': True,
                'added_at': datetime.now().isoformat()
            }
            self._save_global_sources()

            # Also add to config.json so it's available in news_sources
            self._add_to_config_json(name, url, category)

            logger.info(f"Added custom source '{name}' to global sources and config.json")

        except Exception as e:
            logger.error(f"Error adding to global sources: {e}")

    def _add_to_config_json(self, name: str, url: str, category: str):
        """Add source to config.json news_sources"""
        try:
            config_path = os.path.join(os.getcwd(), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # Add to news_sources
                if 'news_sources' not in config:
                    config['news_sources'] = {}

                config['news_sources'][name] = {
                    'url': url,
                    'category': category,
                    'type': 'rss',
                    'added_by_user': True,
                    'added_at': datetime.now().isoformat()
                }

                # Save updated config
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                # Refresh global news_sources variable
                global news_sources
                news_sources = load_news_sources()

                logger.info(f"Added '{name}' to config.json news_sources")
            else:
                logger.error("config.json not found")

        except Exception as e:
            logger.error(f"Error adding to config.json: {e}")

    def get_global_sources(self) -> Dict[str, Any]:
        """Get all global sources (static + user-added)"""
        return self.global_sources

    def get_pending_custom_sources(self) -> List[UserSource]:
        """Get all custom sources pending admin approval"""
        pending_sources = []
        for user_sources in self.user_sources.values():
            for source in user_sources:
                if (source.source_type == SourceType.USER_CUSTOM and
                    source.status == SourceStatus.PENDING_APPROVAL):
                    pending_sources.append(source)

        return pending_sources

    def approve_custom_source(self, source_id: str, admin_user_id: str, tags: List[str] = None) -> Dict[str, Any]:
        """Approve a custom source and optionally add to global sources"""
        try:
            # Find the source
            for user_sources in self.user_sources.values():
                for source in user_sources:
                    if source.source_id == source_id:
                        source.status = SourceStatus.APPROVED
                        source.reviewed_by = admin_user_id
                        source.reviewed_at = datetime.now().isoformat()

                        # Add tags if provided
                        if tags:
                            source.tags = tags

                        # Add to global sources
                        system_settings = self.admin_settings.get_system_settings()
                        if system_settings.auto_add_user_sources_to_global:
                            self._add_to_global_sources(source.name, source.url, source.category)

                        self._save_user_sources()

                        return {'success': True, 'source': source.to_dict()}

            return {'success': False, 'error': 'Source not found'}

        except Exception as e:
            logger.error(f"Error approving custom source: {e}")
            return {'success': False, 'error': 'Failed to approve source'}

    def reject_custom_source(self, source_id: str, admin_user_id: str, reason: str) -> Dict[str, Any]:
        """Reject a custom source with reason"""
        try:
            # Find the source
            for user_sources in self.user_sources.values():
                for source in user_sources:
                    if source.source_id == source_id:
                        source.status = SourceStatus.REJECTED
                        source.rejection_reason = reason
                        source.reviewed_by = admin_user_id
                        source.reviewed_at = datetime.now().isoformat()

                        self._save_user_sources()

                        return {'success': True, 'source': source.to_dict()}

            return {'success': False, 'error': 'Source not found'}

        except Exception as e:
            logger.error(f"Error rejecting custom source: {e}")
            return {'success': False, 'error': 'Failed to reject source'}

    def validate_source(self, url: str, name: str = "", category: str = "") -> Dict[str, Any]:
        """Validate a source using the source validator"""
        try:
            if SourceValidator is None:
                return {
                    'success': False,
                    'error': 'Source validation not available'
                }

            validator = SourceValidator()
            result = validator.validate_source(url, name, category)

            return {
                'success': True,
                'validation_result': result.to_dict()
            }

        except Exception as e:
            logger.error(f"Error validating source: {e}")
            return {
                'success': False,
                'error': f'Validation failed: {str(e)}'
            }
