"""
Call accounting module for EODData client.

This module provides functionality to track API calls, enforce quotas,
and manage accounting data for EODData client usage.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import os


@dataclass
class AccountingData:
    """Data structure for accounting information."""
    
    # Operation-level tracking
    totals: Dict[str, int]  # total_calls, calls_60s, calls_24h
    
    # Metadata
    metadata: Dict[str, Any]
    
    # Status variables
    status: Dict[str, bool]
    
    # Quotas
    quotas: Dict[str, int]


@dataclass
class GlobalData:
    """Global accounting statistics."""
    total_calls: int = 0
    calls_60s: int = 0
    calls_24h: int = 0


class OutOfQuotaError(Exception):
    """Custom exception raised when API call quota is exceeded."""
    
    def __init__(self, message: str, quota_type: str):
        self.message = message
        self.quota_type = quota_type
        super().__init__(self.message)


class AccountingTracker:
    """Tracks API calls and enforces quotas."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.data: List[Dict[str, Any]] = []
        self._last_cleanup_time: Optional[float] = None
        self._is_running = False
        
    def start(self) -> None:
        """Start the accounting tracker."""
        self._is_running = True
        if self.debug:
            print("Accounting tracker started")
    
    def stop(self) -> None:
        """Stop the accounting tracker."""
        self._is_running = False
        if self.debug:
            print("Accounting tracker stopped")
    
    def reset(self) -> None:
        """Reset all counters while preserving quotas."""
        for api_key_data in self.data:
            # Reset counters but preserve quotas
            for operation_id in list(api_key_data.keys()):
                if operation_id not in ['global', 'api_key_masked']:
                    # Reset operation counters
                    api_key_data[operation_id]['totals'] = {
                        'total_calls': 0,
                        'calls_60s': 0,
                        'calls_24h': 0
                    }
                    # Update last updated timestamp
                    api_key_data[operation_id]['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Reset global counters
            if 'global' in api_key_data:
                api_key_data['global'] = {
                    'total_calls': 0,
                    'calls_60s': 0,
                    'calls_24h': 0
                }
        
        if self.debug:
            print("Accounting counters reset")
    
    def _get_api_key_data(self, api_key: str) -> Dict[str, Any]:
        """Get or create data structure for an API key."""
        # Find existing API key data
        for api_key_data in self.data:
            if api_key_data.get('api_key_masked') == self._mask_api_key(api_key):
                return api_key_data
        
        # Create new API key data
        new_api_key_data = {
            'api_key_masked': self._mask_api_key(api_key),
            'global': {
                'total_calls': 0,
                'calls_60s': 0,
                'calls_24h': 0
            }
        }
        self.data.append(new_api_key_data)
        return new_api_key_data
    
    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for display purposes."""
        if len(api_key) <= 8:
            return api_key
        return f"{api_key[:4]}****{api_key[-4:]}"
    
    def increment_call(self, api_key: str, operation_id: str) -> None:
        """Increment call counters for an API key and operation."""
        if not self._is_running:
            return
            
        api_key_data = self._get_api_key_data(api_key)
        
        # Initialize operation if not exists
        if operation_id not in api_key_data:
            api_key_data[operation_id] = {
                'totals': {
                    'total_calls': 0,
                    'calls_60s': 0,
                    'calls_24h': 0
                },
                'metadata': {
                    'started_at': datetime.now().isoformat(),
                    'stopped_at': None,
                    'last_updated': datetime.now().isoformat()
                },
                'status': {
                    'counting_enabled': True,
                    'quotas_enabled': False
                },
                'quotas': {
                    'total': 0,
                    'calls_60s': 0,
                    'calls_24h': 0
                }
            }
        
        # Update operation counters
        operation_data = api_key_data[operation_id]
        current_time = time.time()
        
        # Increment all counters
        operation_data['totals']['total_calls'] += 1
        operation_data['totals']['calls_60s'] += 1
        operation_data['totals']['calls_24h'] += 1
        
        # Update metadata
        operation_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Update global counters
        api_key_data['global']['total_calls'] += 1
        api_key_data['global']['calls_60s'] += 1
        api_key_data['global']['calls_24h'] += 1
        
        # Clean up old data if needed
        self._cleanup_old_data(current_time)
        
        if self.debug:
            print(f"API call incremented for {api_key} operation {operation_id}")
    
    def enable_quotas(self, api_key: str, total: int = 0, calls_60s: int = 0, calls_24h: int = 0) -> None:
        """Enable quotas for an API key."""
        api_key_data = self._get_api_key_data(api_key)
        
        # Set quotas at API key level (not operation level)
        # Since quotas are per API key, we set them for all operations under this key
        for operation_id in api_key_data.keys():
            if operation_id not in ['global', 'api_key_masked']:
                api_key_data[operation_id]['quotas'] = {
                    'total': total,
                    'calls_60s': calls_60s,
                    'calls_24h': calls_24h
                }
                # Enable quota checking for this operation
                api_key_data[operation_id]['status']['quotas_enabled'] = True
        
        if self.debug:
            print(f"Quotas enabled for {api_key}: total={total}, 60s={calls_60s}, 24h={calls_24h}")
    
    def check_quota(self, api_key: str) -> None:
        """Check if API key quotas are exceeded and raise OutOfQuotaError if so."""
        if not self._is_running:
            return
            
        api_key_data = self._get_api_key_data(api_key)
        
        # Check quotas against global totals for this API key
        if 'global' not in api_key_data:
            return
            
        global_stats = api_key_data['global']
        
        # Check if quotas are enabled for any operation
        quotas_enabled = False
        for operation_id in api_key_data.keys():
            if operation_id not in ['global', 'api_key_masked']:
                if api_key_data[operation_id]['status'].get('quotas_enabled', False):
                    quotas_enabled = True
                    break
        
        if not quotas_enabled:
            return
            
        # Check each quota (only if > 0) against global stats
        quotas = {}
        for operation_id in api_key_data.keys():
            if operation_id not in ['global', 'api_key_masked']:
                quotas = api_key_data[operation_id]['quotas']
                break  # All operations should have same quotas
        
        if quotas.get('total', 0) > 0 and global_stats['total_calls'] >= quotas['total']:
            raise OutOfQuotaError(
                f"Out of quota: Total calls ({global_stats['total_calls']}) exceeds limit ({quotas['total']})",
                'total'
            )
        
        if quotas.get('calls_60s', 0) > 0 and global_stats['calls_60s'] >= quotas['calls_60s']:
            raise OutOfQuotaError(
                f"Out of quota: 60s calls ({global_stats['calls_60s']}) exceeds limit ({quotas['calls_60s']})",
                'calls_60s'
            )
        
        if quotas.get('calls_24h', 0) > 0 and global_stats['calls_24h'] >= quotas['calls_24h']:
            raise OutOfQuotaError(
                f"Out of quota: 24h calls ({global_stats['calls_24h']}) exceeds limit ({quotas['calls_24h']})",
                'calls_24h'
            )
    
    def _cleanup_old_data(self, current_time: float) -> None:
        """Remove old data that's outside the 24h window."""
        # Only run cleanup periodically to avoid overhead
        if self._last_cleanup_time is None or (current_time - self._last_cleanup_time) > 3600:  # Every hour
            # In a real implementation, this would clean up old entries
            # For now we just update the timestamp
            self._last_cleanup_time = current_time
    
    def save_to_file(self, filename: Optional[str] = None) -> str:
        """Save accounting data to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"eoddata.accounting.{timestamp}.json"
        
        # Convert dataclasses to dictionaries for JSON serialization
        serialized_data = []
        for api_key_entry in self.data:
            entry_copy = api_key_entry.copy()
            serialized_data.append(entry_copy)
        
        with open(filename, 'w') as f:
            json.dump(serialized_data, f, indent=2)
        
        if self.debug:
            print(f"Accounting data saved to {filename}")
        return filename
    
    def load_from_file(self, filename: str) -> None:
        """Load accounting data from JSON file."""
        try:
            with open(filename, 'r') as f:
                loaded_data = json.load(f)
            
            self.data = loaded_data
            
            if self.debug:
                print(f"Accounting data loaded from {filename}")
        except FileNotFoundError:
            if self.debug:
                print(f"File {filename} not found, starting with empty data")
        except json.JSONDecodeError:
            if self.debug:
                print(f"Invalid JSON in {filename}")
    
    def summary(self) -> str:
        """Generate a readable ASCII summary of accounting data."""
        if not self.data:
            return "No accounting data available"
        
        summary_lines = ["EODData Call Accounting Summary", "=" * 40]
        
        for api_key_data in self.data:
            api_key_masked = api_key_data.get('api_key_masked', 'Unknown')
            summary_lines.append(f"\nAPI Key: {api_key_masked}")
            
            # Show global stats
            if 'global' in api_key_data:
                global_stats = api_key_data['global']
                summary_lines.append(f"  Global Totals:")
                summary_lines.append(f"    Total calls: {global_stats['total_calls']}")
                summary_lines.append(f"    60s calls: {global_stats['calls_60s']}")
                summary_lines.append(f"    24h calls: {global_stats['calls_24h']}")
            
            # Show operation stats
            operations = [k for k in api_key_data.keys() if k not in ['global', 'api_key_masked']]
            if operations:
                summary_lines.append("  Operations:")
                for operation_id in operations:
                    if operation_id in api_key_data:
                        op_data = api_key_data[operation_id]
                        totals = op_data['totals']
                        summary_lines.append(f"    {operation_id}:")
                        summary_lines.append(f"      Total calls: {totals['total_calls']}")
                        summary_lines.append(f"      60s calls: {totals['calls_60s']}")
                        summary_lines.append(f"      24h calls: {totals['calls_24h']}")
            
            # Show quotas if enabled
            summary_lines.append("")
        
        return "\n".join(summary_lines)