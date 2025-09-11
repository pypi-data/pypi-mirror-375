# tests/test_init.py
"""
Tests for EODData package initialization
"""

import pytest
from eoddata import (
    __version__, 
    __author__, 
    EODDataClient, 
    EODDataError, 
    EODDataAPIError, 
    EODDataAuthError,
    AccountingTracker,
    OutOfQuotaError,
    __all__
)


class TestPackageInit:
    """Test package initialization and imports"""

    def test_version_import_success(self):
        """Test successful version import"""
        # Version should be a string
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_author_exists(self):
        """Test that author attribute exists"""
        assert __author__ is not None
        assert isinstance(__author__, str)
        assert __author__ == "Mike Quest"

    def test_all_exports(self):
        """Test __all__ contains expected exports"""
        expected_exports = [
            "EODDataClient", 
            "EODDataError", 
            "EODDataAPIError", 
            "EODDataAuthError",
            "AccountingTracker",
            "OutOfQuotaError"
        ]

        for export in expected_exports:
            assert export in __all__

    def test_imports_available(self):
        """Test all imports are available"""
        # All classes should be importable
        assert EODDataClient is not None
        assert EODDataError is not None
        assert EODDataAPIError is not None
        assert EODDataAuthError is not None
        assert AccountingTracker is not None
        assert OutOfQuotaError is not None

    def test_exception_hierarchy(self):
        """Test exception class hierarchy"""
        # Test that specific exceptions inherit from base
        assert issubclass(EODDataAPIError, EODDataError)
        assert issubclass(EODDataAuthError, EODDataError)

        # Test instantiation
        base_error = EODDataError("Base error")
        api_error = EODDataAPIError("API error") 
        auth_error = EODDataAuthError("Auth error")

        assert str(base_error) == "Base error"
        assert str(api_error) == "API error"
        assert str(auth_error) == "Auth error"

    def test_accounting_classes(self):
        """Test accounting classes are properly imported"""
        # Test AccountingTracker instantiation
        tracker = AccountingTracker(debug=False)
        assert tracker is not None

        # Test OutOfQuotaError instantiation
        error = OutOfQuotaError("Quota exceeded", "daily")
        assert error is not None
        assert str(error) == "Quota exceeded"
        assert error.quota_type == "daily"

    def test_package_metadata(self):
        """Test basic package metadata"""
        # Test that we can import the package successfully
        import eoddata
        assert hasattr(eoddata, '__version__')
        assert hasattr(eoddata, '__author__')
        assert hasattr(eoddata, '__all__')
