# tests/test_api_modules.py
"""
Tests for API module classes and methods
"""

import pytest
from unittest.mock import Mock
from eoddata.api.corporate import CorporateAPI
from eoddata.api.fundamentals import FundamentalsAPI
from eoddata.api.technicals import TechnicalsAPI
from eoddata.api.metadata import MetadataAPI
from eoddata.api.quotes import QuotesAPI
from eoddata.api.symbols import SymbolsAPI
from eoddata.api.exchanges import ExchangesAPI


class TestAPIModules:
    """Test API module classes"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_client._request.return_value = [{"test": "data"}]

    def test_corporate_api_methods(self):
        """Test CorporateAPI methods"""
        api = CorporateAPI(self.mock_client)

        # Test profile_get method
        result = api.profile_get("NASDAQ", "AAPL")
        assert result == [{"test": "data"}]
        self.mock_client._request.assert_called_with("GET", "/Profile/Get/NASDAQ/AAPL")

        # Test profiles_list method
        result = api.profiles_list("NASDAQ")
        self.mock_client._request.assert_called_with("GET", "/Profile/List/NASDAQ")

    def test_corporate_api_splits(self):
        """Test CorporateAPI splits methods"""
        api = CorporateAPI(self.mock_client)

        # Test splits_by_symbol method
        result = api.splits_by_symbol("NASDAQ", "AAPL")
        self.mock_client._request.assert_called_with("GET", "/Splits/List/NASDAQ/AAPL")

        # Test splits_by_exchange method
        result = api.splits_by_exchange("NASDAQ")
        self.mock_client._request.assert_called_with("GET", "/Splits/List/NASDAQ")

    def test_corporate_api_dividends(self):
        """Test CorporateAPI dividends methods"""
        api = CorporateAPI(self.mock_client)

        # Test dividends_by_symbol method
        result = api.dividends_by_symbol("NASDAQ", "AAPL")
        self.mock_client._request.assert_called_with("GET", "/Dividends/List/NASDAQ/AAPL")

        # Test dividends_by_exchange method
        result = api.dividends_by_exchange("NASDAQ")
        self.mock_client._request.assert_called_with("GET", "/Dividends/List/NASDAQ")

    def test_fundamentals_api_methods(self):
        """Test FundamentalsAPI methods"""
        api = FundamentalsAPI(self.mock_client)

        # Test list method - takes only exchange_code
        result = api.list("NASDAQ")
        assert result == [{"test": "data"}]
        self.mock_client._request.assert_called_with("GET", "/Fundamental/List/NASDAQ")

        # Test get method - takes exchange_code and symbol_code
        result = api.get("NASDAQ", "AAPL")
        self.mock_client._request.assert_called_with("GET", "/Fundamental/Get/NASDAQ/AAPL")

    def test_technicals_api_methods(self):
        """Test TechnicalsAPI methods"""
        api = TechnicalsAPI(self.mock_client)

        # Test list method - takes only exchange_code
        result = api.list("NASDAQ")
        assert result == [{"test": "data"}]
        self.mock_client._request.assert_called_with("GET", "/Technical/List/NASDAQ")

    def test_metadata_api_methods(self):
        """Test MetadataAPI methods"""
        api = MetadataAPI(self.mock_client)

        # Test exchange_types method
        result = api.exchange_types()
        self.mock_client._request.assert_called_with("GET", "/ExchangeType/List", params={})

        # Test symbol_types method
        result = api.symbol_types()
        self.mock_client._request.assert_called_with("GET", "/SymbolType/List", params={})

        # Test countries method
        result = api.countries()
        self.mock_client._request.assert_called_with("GET", "/Country/List", params={})

        # Test currencies method
        result = api.currencies()
        self.mock_client._request.assert_called_with("GET", "/Currency/List", params={})

    def test_quotes_api_methods(self):
        """Test QuotesAPI methods"""
        api = QuotesAPI(self.mock_client)

        # Test get method
        result = api.get("NASDAQ", "AAPL")
        self.mock_client._request.assert_called_with("GET", "/Quote/Get/NASDAQ/AAPL", params={})

        # Test list_by_exchange method
        result = api.list_by_exchange("NASDAQ")
        self.mock_client._request.assert_called_with("GET", "/Quote/List/NASDAQ", params={})

        # Test list_by_symbol method
        result = api.list_by_symbol("NASDAQ", "AAPL")
        self.mock_client._request.assert_called_with("GET", "/Quote/List/NASDAQ/AAPL", params={})

    def test_symbols_api_methods(self):
        """Test SymbolsAPI methods"""
        api = SymbolsAPI(self.mock_client)

        result = api.list("NASDAQ")
        self.mock_client._request.assert_called_with("GET", "/Symbol/List/NASDAQ")

    def test_exchanges_api_methods(self):
        """Test ExchangesAPI methods"""
        api = ExchangesAPI(self.mock_client)

        result = api.list()
        self.mock_client._request.assert_called_with("GET", "/Exchange/List")

    def test_base_api_initialization(self):
        """Test BaseAPI initialization"""
        from eoddata.api.base import BaseAPI

        api = BaseAPI(self.mock_client)
        assert api.client is self.mock_client
