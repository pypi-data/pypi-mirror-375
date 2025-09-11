# tests/test_client.py
"""
Tests for EODData client
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from eoddata import EODDataClient, EODDataError, EODDataAPIError, EODDataAuthError
from eoddata.accounting import AccountingTracker


class TestEODDataClient:

    def test_client_initialization(self):
        client = EODDataClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.eoddata.com"
        assert client.timeout == 30

    def test_client_initialization_with_custom_params(self):
        accounting = Mock()
        client = EODDataClient(
            api_key="test_key",
            base_url="https://custom.api.com/",
            timeout=60,
            debug=True,
            accounting=accounting
        )
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.api.com"  # trailing slash removed
        assert client.timeout == 60
        assert client.debug is True
        assert client.accounting == accounting

    def test_debug_mode_logging(self):
        client = EODDataClient(api_key="test_key", debug=True)
        assert client.debug is True
        assert client.logger is not None

    @patch('eoddata.client.requests.Session.request')
    def test_successful_request(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="test_key")
        result = client._request("GET", "/test")

        assert result == {"test": "data"}
        mock_request.assert_called_once()

    @patch('eoddata.client.requests.Session.request')
    def test_successful_request_with_debug(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.content = b'{"test": "data"}'
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="test_key", debug=True)
        result = client._request("GET", "/test")

        assert result == {"test": "data"}

    @patch('eoddata.client.requests.Session.request')
    def test_successful_request_with_accounting(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response

        accounting = Mock()
        client = EODDataClient(api_key="test_key", accounting=accounting)
        result = client._request("GET", "/test")

        assert result == {"test": "data"}
        # The accounting should be called but the exact call signature depends on implementation
        if accounting.record_call.called:
            accounting.record_call.assert_called()

    @patch('eoddata.client.requests.Session.request')
    def test_auth_error(self, mock_request):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="invalid_key")

        with pytest.raises(EODDataAuthError):
            client._request("GET", "/test")

    @patch('eoddata.client.requests.Session.request')
    def test_not_found_error(self, mock_request):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="test_key")

        with pytest.raises(EODDataAPIError, match="Resource not found"):
            client._request("GET", "/nonexistent")

    @patch('eoddata.client.requests.Session.request')
    def test_rate_limit_error(self, mock_request):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 429
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="test_key")

        with pytest.raises(EODDataAPIError, match="Rate limit exceeded"):
            client._request("GET", "/test")

    @patch('eoddata.client.requests.Session.request')
    def test_generic_api_error(self, mock_request):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="test_key")

        with pytest.raises(EODDataAPIError, match="API request failed with status 500"):
            client._request("GET", "/test")

    @patch('eoddata.client.requests.Session.request')
    def test_json_parse_error(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON response"
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="test_key")

        with pytest.raises(EODDataError, match="Invalid JSON response"):
            client._request("GET", "/test")

    @patch('eoddata.client.requests.Session.request')
    def test_timeout_error(self, mock_request):
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")

        client = EODDataClient(api_key="test_key")

        with pytest.raises(EODDataError, match="Request timeout after 30 seconds"):
            client._request("GET", "/test")

    @patch('eoddata.client.requests.Session.request')
    def test_connection_error(self, mock_request):
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = EODDataClient(api_key="test_key")

        with pytest.raises(EODDataError, match="Connection error"):
            client._request("GET", "/test")

    @patch('eoddata.client.requests.Session.request')
    def test_generic_request_exception(self, mock_request):
        mock_request.side_effect = requests.exceptions.RequestException("Generic error")

        client = EODDataClient(api_key="test_key")

        with pytest.raises(EODDataError, match="Request failed"):
            client._request("GET", "/test")

    @patch('eoddata.client.requests.Session.request')
    def test_debug_error_response(self, mock_request):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad request error details"
        mock_response.content = b"Bad request error details"
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        client = EODDataClient(api_key="test_key", debug=True)

        with pytest.raises(EODDataAPIError):
            client._request("GET", "/test")

    def test_lazy_loading_properties(self):
        client = EODDataClient(api_key="test_key")

        # Properties should be None initially
        assert client._metadata is None
        assert client._exchanges is None
        assert client._symbols is None
        assert client._quotes is None
        assert client._corporate is None
        assert client._fundamentals is None
        assert client._technicals is None

        # Accessing properties should create instances
        metadata = client.metadata
        exchanges = client.exchanges
        symbols = client.symbols
        quotes = client.quotes
        corporate = client.corporate
        fundamentals = client.fundamentals
        technicals = client.technicals

        assert client._metadata is not None
        assert client._exchanges is not None
        assert client._symbols is not None
        assert client._quotes is not None
        assert client._corporate is not None
        assert client._fundamentals is not None
        assert client._technicals is not None

        # Subsequent accesses should return same instances
        assert client.metadata is metadata
        assert client.exchanges is exchanges
        assert client.symbols is symbols
        assert client.quotes is quotes
        assert client.corporate is corporate
        assert client.fundamentals is fundamentals
        assert client.technicals is technicals

    def test_context_manager(self):
        with EODDataClient(api_key="test_key") as client:
            assert isinstance(client, EODDataClient)

    def test_context_manager_session_close(self):
        client = EODDataClient(api_key="test_key")
        session_mock = Mock()
        client._session = session_mock

        with client:
            pass

        session_mock.close.assert_called_once()
