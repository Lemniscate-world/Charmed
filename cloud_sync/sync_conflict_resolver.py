"""
sync_conflict_resolver.py - Conflict resolution for cloud synchronization

This module provides conflict resolution strategies when multiple devices
have conflicting data:
- Timestamp-based resolution (newest wins)
- Manual resolution with user prompts
- Merge strategies for non-conflicting changes
- Conflict detection and reporting
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import get_logger

logger = get_logger(__name__)


class SyncConflictResolver:
    """
    Resolver for synchronization conflicts between devices.
    
    Provides various strategies for resolving conflicts when
    multiple devices have different versions of the same data.
    """
    
    STRATEGY_NEWEST_WINS = 'newest_wins'
    STRATEGY_LOCAL_WINS = 'local_wins'
    STRATEGY_REMOTE_WINS = 'remote_wins'
    STRATEGY_MERGE = 'merge'
    STRATEGY_MANUAL = 'manual'
    
    def __init__(self, default_strategy: str = STRATEGY_NEWEST_WINS):
        """
        Initialize conflict resolver.
        
        Args:
            default_strategy: Default conflict resolution strategy
        """
        self.default_strategy = default_strategy
        logger.info(f'SyncConflictResolver initialized with strategy: {default_strategy}')
    
    def detect_conflicts(self, local_data: List[Dict], remote_data: List[Dict]) -> Tuple[bool, List[Dict]]:
        """
        Detect conflicts between local and remote data.
        
        Args:
            local_data: Local alarm/settings data
            remote_data: Remote alarm/settings data
            
        Returns:
            Tuple of (has_conflicts, conflicts_list)
        """
        conflicts = []
        
        # Build index of local data by time or ID
        local_index = {self._get_data_key(item): item for item in local_data}
        remote_index = {self._get_data_key(item): item for item in remote_data}
        
        # Find conflicts (items that exist in both but differ)
        for key, local_item in local_index.items():
            if key in remote_index:
                remote_item = remote_index[key]
                if self._items_differ(local_item, remote_item):
                    conflicts.append({
                        'key': key,
                        'local': local_item,
                        'remote': remote_item,
                        'conflict_type': self._determine_conflict_type(local_item, remote_item)
                    })
        
        has_conflicts = len(conflicts) > 0
        
        if has_conflicts:
            logger.info(f"Detected {len(conflicts)} conflicts")
        
        return has_conflicts, conflicts
    
    def resolve_conflicts(self, conflicts: List[Dict], strategy: Optional[str] = None) -> List[Dict]:
        """
        Resolve conflicts using specified strategy.
        
        Args:
            conflicts: List of conflict dictionaries
            strategy: Resolution strategy (uses default if None)
            
        Returns:
            List of resolved data items
        """
        strategy = strategy or self.default_strategy
        resolved = []
        
        for conflict in conflicts:
            if strategy == self.STRATEGY_NEWEST_WINS:
                resolved.append(self._resolve_newest_wins(conflict))
            elif strategy == self.STRATEGY_LOCAL_WINS:
                resolved.append(conflict['local'])
            elif strategy == self.STRATEGY_REMOTE_WINS:
                resolved.append(conflict['remote'])
            elif strategy == self.STRATEGY_MERGE:
                resolved.append(self._resolve_merge(conflict))
            elif strategy == self.STRATEGY_MANUAL:
                # Manual resolution requires user interaction
                # Return both versions for user to choose
                resolved.append({
                    'conflict': True,
                    'local': conflict['local'],
                    'remote': conflict['remote'],
                    'key': conflict['key']
                })
            else:
                logger.warning(f"Unknown strategy {strategy}, using newest wins")
                resolved.append(self._resolve_newest_wins(conflict))
        
        logger.info(f"Resolved {len(resolved)} conflicts using strategy: {strategy}")
        return resolved
    
    def merge_data(self, local_data: List[Dict], remote_data: List[Dict], strategy: Optional[str] = None) -> Tuple[List[Dict], int]:
        """
        Merge local and remote data, resolving conflicts.
        
        Args:
            local_data: Local data items
            remote_data: Remote data items
            strategy: Conflict resolution strategy
            
        Returns:
            Tuple of (merged_data, num_conflicts)
        """
        strategy = strategy or self.default_strategy
        
        # Detect conflicts
        has_conflicts, conflicts = self.detect_conflicts(local_data, remote_data)
        
        if not has_conflicts:
            # No conflicts, simple merge
            logger.info("No conflicts detected, performing simple merge")
            return self._simple_merge(local_data, remote_data), 0
        
        # Resolve conflicts
        resolved = self.resolve_conflicts(conflicts, strategy)
        
        # Build merged data
        merged = self._build_merged_data(local_data, remote_data, resolved, conflicts)
        
        logger.info(f"Merged data with {len(conflicts)} conflicts resolved")
        return merged, len(conflicts)
    
    def _get_data_key(self, item: Dict) -> str:
        """
        Get unique key for a data item.
        
        For alarms: uses time + playlist as key
        For settings: uses setting name as key
        """
        if 'time' in item and 'playlist' in item:
            # Alarm item
            return f"{item.get('time', '')}:{item.get('playlist', '')}"
        elif 'name' in item:
            # Settings item
            return item.get('name', '')
        else:
            # Generic item
            return str(hash(str(item)))
    
    def _items_differ(self, item1: Dict, item2: Dict) -> bool:
        """Check if two items differ (excluding timestamps)."""
        # Compare items excluding metadata fields
        exclude_keys = {'last_modified', 'device_id', 'sync_time'}
        
        keys1 = set(k for k in item1.keys() if k not in exclude_keys)
        keys2 = set(k for k in item2.keys() if k not in exclude_keys)
        
        if keys1 != keys2:
            return True
        
        for key in keys1:
            if item1[key] != item2[key]:
                return True
        
        return False
    
    def _determine_conflict_type(self, local_item: Dict, remote_item: Dict) -> str:
        """Determine the type of conflict."""
        # Check which fields differ
        differing_fields = []
        
        all_keys = set(local_item.keys()) | set(remote_item.keys())
        for key in all_keys:
            if key in {'last_modified', 'device_id', 'sync_time'}:
                continue
            
            local_val = local_item.get(key)
            remote_val = remote_item.get(key)
            
            if local_val != remote_val:
                differing_fields.append(key)
        
        if not differing_fields:
            return 'metadata_only'
        elif len(differing_fields) == 1:
            return f'field_conflict:{differing_fields[0]}'
        else:
            return 'multiple_fields'
    
    def _resolve_newest_wins(self, conflict: Dict) -> Dict:
        """Resolve conflict by choosing newest item based on timestamp."""
        local = conflict['local']
        remote = conflict['remote']
        
        local_time = local.get('last_modified') or local.get('timestamp', '')
        remote_time = remote.get('last_modified') or remote.get('timestamp', '')
        
        try:
            local_dt = datetime.fromisoformat(local_time) if local_time else datetime.min
            remote_dt = datetime.fromisoformat(remote_time) if remote_time else datetime.min
            
            if remote_dt > local_dt:
                logger.debug(f"Conflict resolved: remote wins (newer)")
                return remote
            else:
                logger.debug(f"Conflict resolved: local wins (newer)")
                return local
        except Exception as e:
            logger.warning(f"Error parsing timestamps, defaulting to local: {e}")
            return local
    
    def _resolve_merge(self, conflict: Dict) -> Dict:
        """Resolve conflict by merging non-conflicting fields."""
        local = conflict['local'].copy()
        remote = conflict['remote']
        
        # Use newest timestamp as base
        resolved = self._resolve_newest_wins(conflict).copy()
        
        # Validate that critical alarm fields are present
        if 'time' in local or 'time' in remote:
            if 'time' not in resolved or 'playlist_uri' not in resolved:
                logger.warning("Merged alarm missing critical fields, using complete version")
                resolved = local if ('time' in local and 'playlist_uri' in local) else remote
        
        # For specific fields, merge intelligently
        # Example: for alarm days, merge the day lists
        if 'days' in local and 'days' in remote:
            local_days = set(local.get('days', []) or [])
            remote_days = set(remote.get('days', []) or [])
            merged_days = list(local_days | remote_days)
            if merged_days:
                resolved['days'] = merged_days
        
        logger.debug(f"Conflict resolved: merged")
        return resolved
    
    def _simple_merge(self, local_data: List[Dict], remote_data: List[Dict]) -> List[Dict]:
        """Perform simple merge when no conflicts exist."""
        # Build indices
        local_index = {self._get_data_key(item): item for item in local_data}
        remote_index = {self._get_data_key(item): item for item in remote_data}
        
        # Combine all items
        all_keys = set(local_index.keys()) | set(remote_index.keys())
        
        merged = []
        for key in all_keys:
            if key in local_index and key in remote_index:
                # Item exists in both, use local (they're the same)
                merged.append(local_index[key])
            elif key in local_index:
                # Local only
                merged.append(local_index[key])
            else:
                # Remote only
                merged.append(remote_index[key])
        
        return merged
    
    def _build_merged_data(self, local_data: List[Dict], remote_data: List[Dict], 
                          resolved: List[Dict], conflicts: List[Dict]) -> List[Dict]:
        """Build final merged data from local, remote, and resolved conflicts."""
        # Build index of conflict keys
        conflict_keys = {c['key'] for c in conflicts}
        
        # Start with resolved conflicts
        merged = resolved.copy()
        
        # Add non-conflicting local items
        for item in local_data:
            key = self._get_data_key(item)
            if key not in conflict_keys:
                # Check if not in remote
                remote_keys = {self._get_data_key(r) for r in remote_data}
                if key not in remote_keys:
                    merged.append(item)
        
        # Add remote-only items
        for item in remote_data:
            key = self._get_data_key(item)
            if key not in conflict_keys:
                # Check if not in local
                local_keys = {self._get_data_key(l) for l in local_data}
                if key not in local_keys:
                    merged.append(item)
        
        return merged
    
    def prepare_conflict_report(self, conflicts: List[Dict]) -> str:
        """
        Prepare human-readable conflict report.
        
        Args:
            conflicts: List of conflicts
            
        Returns:
            Formatted conflict report string
        """
        if not conflicts:
            return "No conflicts detected."
        
        report = f"Found {len(conflicts)} conflicts:\n\n"
        
        for i, conflict in enumerate(conflicts, 1):
            report += f"Conflict {i}:\n"
            report += f"  Key: {conflict['key']}\n"
            report += f"  Type: {conflict['conflict_type']}\n"
            
            local = conflict['local']
            remote = conflict['remote']
            
            report += f"  Local: {self._format_item(local)}\n"
            report += f"  Remote: {self._format_item(remote)}\n"
            report += "\n"
        
        return report
    
    def _format_item(self, item: Dict) -> str:
        """Format item for display in conflict report."""
        if 'time' in item and 'playlist' in item:
            # Alarm
            return f"Alarm at {item.get('time')} - {item.get('playlist')} (Volume: {item.get('volume', 'N/A')}%)"
        else:
            # Generic
            return str(item)
