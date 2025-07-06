"""
Saved Searches Manager
Handles saving, loading, and managing user search queries
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from .search_engine import SearchQuery


@dataclass
class SavedSearch:
    """Represents a saved search query"""
    id: str
    name: str
    query: SearchQuery
    created_at: datetime
    last_used: Optional[datetime] = None
    use_count: int = 0
    is_favorite: bool = False
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class SavedSearchManager:
    """Manages saved search queries"""
    
    def __init__(self, storage_file: str = "saved_searches.json"):
        self.storage_file = storage_file
        self.searches: Dict[str, SavedSearch] = {}
        self.load_searches()
    
    def save_search(self, name: str, query: SearchQuery, tags: List[str] = None) -> str:
        """
        Save a search query
        
        Args:
            name: Human-readable name for the search
            query: SearchQuery object to save
            tags: Optional tags for categorization
            
        Returns:
            ID of the saved search
        """
        search_id = self._generate_id()
        
        saved_search = SavedSearch(
            id=search_id,
            name=name,
            query=query,
            created_at=datetime.now(),
            tags=tags or []
        )
        
        self.searches[search_id] = saved_search
        self._save_to_file()
        
        return search_id
    
    def get_search(self, search_id: str) -> Optional[SavedSearch]:
        """Get a saved search by ID"""
        return self.searches.get(search_id)
    
    def get_all_searches(self, include_favorites_first: bool = True) -> List[SavedSearch]:
        """
        Get all saved searches
        
        Args:
            include_favorites_first: Whether to sort favorites first
            
        Returns:
            List of SavedSearch objects
        """
        searches = list(self.searches.values())
        
        if include_favorites_first:
            searches.sort(key=lambda x: (not x.is_favorite, x.last_used or x.created_at), reverse=True)
        else:
            searches.sort(key=lambda x: x.last_used or x.created_at, reverse=True)
        
        return searches
    
    def update_search(self, search_id: str, name: str = None, query: SearchQuery = None, 
                     tags: List[str] = None, is_favorite: bool = None) -> bool:
        """
        Update a saved search
        
        Args:
            search_id: ID of the search to update
            name: New name (optional)
            query: New query (optional)
            tags: New tags (optional)
            is_favorite: New favorite status (optional)
            
        Returns:
            True if updated successfully, False if search not found
        """
        if search_id not in self.searches:
            return False
        
        search = self.searches[search_id]
        
        if name is not None:
            search.name = name
        if query is not None:
            search.query = query
        if tags is not None:
            search.tags = tags
        if is_favorite is not None:
            search.is_favorite = is_favorite
        
        self._save_to_file()
        return True
    
    def delete_search(self, search_id: str) -> bool:
        """
        Delete a saved search
        
        Args:
            search_id: ID of the search to delete
            
        Returns:
            True if deleted successfully, False if search not found
        """
        if search_id in self.searches:
            del self.searches[search_id]
            self._save_to_file()
            return True
        return False
    
    def use_search(self, search_id: str) -> Optional[SearchQuery]:
        """
        Mark a search as used and return the query
        
        Args:
            search_id: ID of the search to use
            
        Returns:
            SearchQuery object if found, None otherwise
        """
        if search_id not in self.searches:
            return None
        
        search = self.searches[search_id]
        search.last_used = datetime.now()
        search.use_count += 1
        
        self._save_to_file()
        return search.query
    
    def search_by_name(self, name_pattern: str) -> List[SavedSearch]:
        """
        Search saved searches by name pattern
        
        Args:
            name_pattern: Pattern to search for in names
            
        Returns:
            List of matching SavedSearch objects
        """
        pattern_lower = name_pattern.lower()
        matches = []
        
        for search in self.searches.values():
            if pattern_lower in search.name.lower():
                matches.append(search)
        
        return sorted(matches, key=lambda x: x.last_used or x.created_at, reverse=True)
    
    def get_searches_by_tag(self, tag: str) -> List[SavedSearch]:
        """
        Get saved searches by tag
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of SavedSearch objects with the specified tag
        """
        matches = []
        
        for search in self.searches.values():
            if tag in search.tags:
                matches.append(search)
        
        return sorted(matches, key=lambda x: x.last_used or x.created_at, reverse=True)
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags used in saved searches"""
        all_tags = set()
        
        for search in self.searches.values():
            all_tags.update(search.tags)
        
        return sorted(list(all_tags))
    
    def get_popular_searches(self, limit: int = 10) -> List[SavedSearch]:
        """
        Get most popular saved searches by use count
        
        Args:
            limit: Maximum number of searches to return
            
        Returns:
            List of SavedSearch objects sorted by use count
        """
        searches = list(self.searches.values())
        searches.sort(key=lambda x: x.use_count, reverse=True)
        return searches[:limit]
    
    def get_recent_searches(self, limit: int = 10) -> List[SavedSearch]:
        """
        Get recently used saved searches
        
        Args:
            limit: Maximum number of searches to return
            
        Returns:
            List of SavedSearch objects sorted by last use
        """
        searches = [s for s in self.searches.values() if s.last_used]
        searches.sort(key=lambda x: x.last_used, reverse=True)
        return searches[:limit]
    
    def export_searches(self, file_path: str) -> bool:
        """
        Export saved searches to a file
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'searches': []
            }
            
            for search in self.searches.values():
                search_data = {
                    'id': search.id,
                    'name': search.name,
                    'query': asdict(search.query),
                    'created_at': search.created_at.isoformat(),
                    'last_used': search.last_used.isoformat() if search.last_used else None,
                    'use_count': search.use_count,
                    'is_favorite': search.is_favorite,
                    'tags': search.tags
                }
                export_data['searches'].append(search_data)
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def import_searches(self, file_path: str, merge: bool = True) -> bool:
        """
        Import saved searches from a file
        
        Args:
            file_path: Path to import file
            merge: Whether to merge with existing searches or replace
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            if not merge:
                self.searches.clear()
            
            for search_data in import_data.get('searches', []):
                # Reconstruct SearchQuery
                query_data = search_data['query']
                query = SearchQuery(
                    text=query_data.get('text', ''),
                    sources=query_data.get('sources', []),
                    categories=query_data.get('categories', []),
                    date_from=datetime.fromisoformat(query_data['date_from']) if query_data.get('date_from') else None,
                    date_to=datetime.fromisoformat(query_data['date_to']) if query_data.get('date_to') else None,
                    sentiment=query_data.get('sentiment'),
                    min_relevance=query_data.get('min_relevance', 0.0),
                    sort_by=query_data.get('sort_by', 'relevance'),
                    sort_order=query_data.get('sort_order', 'desc'),
                    limit=query_data.get('limit', 50)
                )
                
                # Reconstruct SavedSearch
                saved_search = SavedSearch(
                    id=search_data['id'],
                    name=search_data['name'],
                    query=query,
                    created_at=datetime.fromisoformat(search_data['created_at']),
                    last_used=datetime.fromisoformat(search_data['last_used']) if search_data.get('last_used') else None,
                    use_count=search_data.get('use_count', 0),
                    is_favorite=search_data.get('is_favorite', False),
                    tags=search_data.get('tags', [])
                )
                
                self.searches[saved_search.id] = saved_search
            
            self._save_to_file()
            return True
        except Exception:
            return False
    
    def load_searches(self):
        """Load saved searches from file"""
        if not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            for search_data in data.get('searches', []):
                # Reconstruct SearchQuery
                query_data = search_data['query']
                query = SearchQuery(
                    text=query_data.get('text', ''),
                    sources=query_data.get('sources', []),
                    categories=query_data.get('categories', []),
                    date_from=datetime.fromisoformat(query_data['date_from']) if query_data.get('date_from') else None,
                    date_to=datetime.fromisoformat(query_data['date_to']) if query_data.get('date_to') else None,
                    sentiment=query_data.get('sentiment'),
                    min_relevance=query_data.get('min_relevance', 0.0),
                    sort_by=query_data.get('sort_by', 'relevance'),
                    sort_order=query_data.get('sort_order', 'desc'),
                    limit=query_data.get('limit', 50)
                )
                
                # Reconstruct SavedSearch
                saved_search = SavedSearch(
                    id=search_data['id'],
                    name=search_data['name'],
                    query=query,
                    created_at=datetime.fromisoformat(search_data['created_at']),
                    last_used=datetime.fromisoformat(search_data['last_used']) if search_data.get('last_used') else None,
                    use_count=search_data.get('use_count', 0),
                    is_favorite=search_data.get('is_favorite', False),
                    tags=search_data.get('tags', [])
                )
                
                self.searches[saved_search.id] = saved_search
        
        except Exception:
            # If loading fails, start with empty searches
            self.searches = {}
    
    def _save_to_file(self):
        """Save searches to file"""
        try:
            data = {
                'version': '1.0',
                'saved_at': datetime.now().isoformat(),
                'searches': []
            }
            
            for search in self.searches.values():
                search_data = {
                    'id': search.id,
                    'name': search.name,
                    'query': asdict(search.query),
                    'created_at': search.created_at.isoformat(),
                    'last_used': search.last_used.isoformat() if search.last_used else None,
                    'use_count': search.use_count,
                    'is_favorite': search.is_favorite,
                    'tags': search.tags
                }
                data['searches'].append(search_data)
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass  # Fail silently for now
    
    def _generate_id(self) -> str:
        """Generate a unique ID for a saved search"""
        import uuid
        return str(uuid.uuid4())[:8]
