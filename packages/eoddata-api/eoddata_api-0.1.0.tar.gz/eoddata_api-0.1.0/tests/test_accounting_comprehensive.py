# tests/test_accounting_comprehensive.py
"""
Comprehensive tests for accounting functionality
"""

import os
import pytest
from eoddata.accounting import AccountingTracker, OutOfQuotaError


class TestAccountingComprehensive:

    def test_comprehensive_accounting(self):
        """Test all accounting functionality including save/load"""
        # Create tracker
        accounting = AccountingTracker(debug=True)
        accounting.start()

        # Test basic counter tracking
        accounting.increment_call("test_api_key_12345", "get_quotes")
        accounting.increment_call("test_api_key_12345", "get_quotes")
        accounting.increment_call("test_api_key_12345", "get_symbols")
        accounting.increment_call("test_api_key_98765", "get_exchanges")

        # Test quota enforcement (set 60s quota to 4 since we have 3 calls)
        accounting.enable_quotas("test_api_key_12345", total=5, calls_60s=4, calls_24h=10)
        
        # Should not raise error (within limits)
        accounting.check_quota("test_api_key_12345")

        # Test quota violation detection - add 2 more calls (total will be 5, exceeding quota of 4 for 60s)
        for i in range(2):
            accounting.increment_call("test_api_key_12345", "get_quotes")

        # Should now raise error (60s quota exceeded)
        with pytest.raises(OutOfQuotaError):
            accounting.check_quota("test_api_key_12345")

        # Test summary generation
        summary = accounting.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

        # Test save to file
        filename = accounting.save_to_file()
        assert os.path.exists(filename)

        # Test reset functionality
        accounting.reset()
        summary_after_reset = accounting.summary()
        assert isinstance(summary_after_reset, str)

        # Test load from file
        accounting.load_from_file(filename)
        summary_after_load = accounting.summary()
        assert isinstance(summary_after_load, str)

        # Test stop functionality
        accounting.stop()

        # Test custom filename save
        custom_filename = "test_accounting_data.json"
        accounting.save_to_file(custom_filename)
        assert os.path.exists(custom_filename)

        # Cleanup
        if os.path.exists(custom_filename):
            os.remove(custom_filename)
        if os.path.exists(filename):
            os.remove(filename)
