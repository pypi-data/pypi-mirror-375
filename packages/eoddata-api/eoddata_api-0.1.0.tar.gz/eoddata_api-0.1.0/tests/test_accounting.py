# tests/test_accounting.py
"""
Tests for accounting functionality
"""

import pytest
from eoddata.accounting import AccountingTracker, OutOfQuotaError


class TestAccounting:

    def test_accounting_basic(self):
        """Test basic accounting functionality"""
        # Create tracker
        tracker = AccountingTracker(debug=True)
        
        # Start tracking
        tracker.start()
        
        # Increment some calls
        tracker.increment_call("test_api_key_12345", "get_quotes")
        tracker.increment_call("test_api_key_12345", "get_quotes")
        tracker.increment_call("test_api_key_12345", "get_symbols")
        
        # Check summary
        summary = tracker.summary()
        assert isinstance(summary, str)
        
        # Test quota checking (should not raise error - no quotas enabled)
        tracker.check_quota("test_api_key_12345")
        
        # Enable quotas (set 60s quota to 4 since we have 3 calls)
        tracker.enable_quotas("test_api_key_12345", total=5, calls_60s=4, calls_24h=10)
        
        # Test quota checking (should not raise error - within limits)
        tracker.check_quota("test_api_key_12345")
        
        # Stop tracking
        tracker.stop()
