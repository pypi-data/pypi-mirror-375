# tests/test_comprehensive.py
"""
Comprehensive tests for all EODData API endpoints
"""

import pytest
from unittest.mock import Mock, patch
from eoddata import EODDataClient, EODDataError, EODDataAPIError, EODDataAuthError


class TestEODDataComprehensive:
    
    def test_metadata_api_endpoints(self):
        """Test metadata API endpoints"""
        with patch('eoddata.client.requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = {"exchange_types": ["STOCK", "ETF"]}
            mock_request.return_value = mock_response
            
            client = EODDataClient(api_key="test_key")
            result = client.metadata.exchange_types()
            
            assert result == {"exchange_types": ["STOCK", "ETF"]}
            mock_request.assert_called_once()
    
    def test_exchanges_api_endpoints(self):
        """Test exchanges API endpoints"""
        with patch('eoddata.client.requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = [{"code": "NASDAQ", "name": "NASDAQ"}]
            mock_request.return_value = mock_response
            
            client = EODDataClient(api_key="test_key")
            result = client.exchanges.list()
            
            assert result == [{"code": "NASDAQ", "name": "NASDAQ"}]
            mock_request.assert_called_once()
    
    def test_symbols_api_endpoints(self):
        """Test symbols API endpoints"""
        with patch('eoddata.client.requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = [{"symbol": "AAPL", "name": "Apple Inc."}]
            mock_request.return_value = mock_response
            
            client = EODDataClient(api_key="test_key")
            result = client.symbols.list("NASDAQ")
            
            assert result == [{"symbol": "AAPL", "name": "Apple Inc."}]
            mock_request.assert_called_once()
    
    def test_quotes_api_endpoints(self):
        """Test quotes API endpoints"""
        with patch('eoddata.client.requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"symbol": "AAPL", "open": 150.0, "high": 155.0}
            ]
            mock_request.return_value = mock_response
            
            client = EODDataClient(api_key="test_key")
            
            # Test list_by_exchange
            result1 = client.quotes.list_by_exchange("NASDAQ")
            assert result1 == [{"symbol": "AAPL", "open": 150.0, "high": 155.0}]
            
            # Test get
            result2 = client.quotes.get("NASDAQ", "AAPL")
            assert result2 == [{"symbol": "AAPL", "open": 150.0, "high": 155.0}]
            
            # Test list_by_symbol
            result3 = client.quotes.list_by_symbol("NASDAQ", "AAPL")
            assert result3 == [{"symbol": "AAPL", "open": 150.0, "high": 155.0}]
            
            # Verify all calls were made
            assert mock_request.call_count == 3
    
    def test_corporate_api_endpoints(self):
        """Test corporate API endpoints"""
        with patch('eoddata.client.requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "company_name": "Apple Inc.",
                "sector": "Technology"
            }
            mock_request.return_value = mock_response
            
            client = EODDataClient(api_key="test_key")
            result = client.corporate.profile_get("NASDAQ", "AAPL")
            
            assert result == {
                "company_name": "Apple Inc.",
                "sector": "Technology"
            }
            mock_request.assert_called_once()
    
    def test_fundamentals_api_endpoints(self):
        """Test fundamentals API endpoints"""
        with patch('eoddata.client.requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "pe_ratio": 25.5,
                "eps": 5.8
            }
            mock_request.return_value = mock_response
            
            client = EODDataClient(api_key="test_key")
            result = client.fundamentals.get("NASDAQ", "AAPL")
            
            assert result == {
                "pe_ratio": 25.5,
                "eps": 5.8
            }
            mock_request.assert_called_once()
    
    def test_technicals_api_endpoints(self):
        """Test technicals API endpoints"""
        with patch('eoddata.client.requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "sma_20": 150.5,
                "rsi": 60.2
            }
            mock_request.return_value = mock_response
            
            client = EODDataClient(api_key="test_key")
            result = client.technicals.get("NASDAQ", "AAPL")
            
            assert result == {
                "sma_20": 150.5,
                "rsi": 60.2
            }
            mock_request.assert_called_once()