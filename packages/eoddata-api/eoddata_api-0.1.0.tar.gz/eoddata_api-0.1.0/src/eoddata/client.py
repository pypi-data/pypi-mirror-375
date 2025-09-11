"""
Main client class for EODData API
"""

import requests
import logging
from typing import Optional, Any
from .exceptions import EODDataError, EODDataAPIError, EODDataAuthError
from . import __version__
from .api.metadata import MetadataAPI
from .api.exchanges import ExchangesAPI
from .api.symbols import SymbolsAPI
from .api.quotes import QuotesAPI
from .api.corporate import CorporateAPI
from .api.fundamentals import FundamentalsAPI
from .api.technicals import TechnicalsAPI


class EODDataClient:
    """
    Main client for EODData API

    Args:
        api_key (str): Your EODData API key
        base_url (str): Base URL for the API (default: official EODData API)
        timeout (int): Request timeout in seconds (default: 30)
        debug (bool): Enable verbose logging of requests and responses (default: False)
        accounting (AccountingTracker, optional): Accounting tracker instance for call tracking

    Example:
        >>> client = EODDataClient(api_key="your_api_key")
        >>> exchanges = client.exchanges.list()
        >>> quotes = client.quotes.list_by_exchange("NASDAQ")

        >>> # Enable debug mode for troubleshooting
        >>> client = EODDataClient(api_key="your_api_key", debug=True)
        >>> exchanges = client.exchanges.list()  # Will log request/response details
        
        >>> # Enable accounting
        >>> from eoddata.accounting import AccountingTracker
        >>> accounting = AccountingTracker(debug=True)
        >>> accounting.start()
        >>> client = EODDataClient(api_key="your_api_key", accounting=accounting)
    """

    def __init__(self, api_key: str, base_url: str = "https://api.eoddata.com", timeout: int = 30, debug: bool = False, accounting: Optional[Any] = None):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.debug = debug
        self.accounting = accounting
        self.accounting = accounting
        self.accounting = accounting

        # Set up logger for debug mode
        self.logger = logging.getLogger('eoddata.client')
        if self.debug:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.logger.setLevel(logging.DEBUG)

        # Check for default placeholder API key
        if self.api_key == "PLACE_YOUR_API_KEY_HERE":
            raise ValueError(
                "API key is still set to the placeholder value. "
                "Please edit your .env file and replace it with a real EODData API key. "
                "You can get one at https://eoddata.com/products/api.aspx"
            )

        # Lazy-loaded API categories
        self._metadata = None
        self._exchanges = None
        self._symbols = None
        self._quotes = None
        self._corporate = None
        self._fundamentals = None
        self._technicals = None

        # Session for connection pooling
        self._session = requests.Session()
        # Set proper User-Agent identifying this Python client
        self._session.headers.update({
            'User-Agent': f'eoddata-python/{__version__} (Python API Client; https://github.com/vrontier/eoddata)'
        })

    @property
    def metadata(self) -> MetadataAPI:
        """Access metadata API endpoints"""
        if self._metadata is None:
            self._metadata = MetadataAPI(self)
        return self._metadata

    @property
    def exchanges(self) -> ExchangesAPI:
        """Access exchanges API endpoints"""
        if self._exchanges is None:
            self._exchanges = ExchangesAPI(self)
        return self._exchanges

    @property
    def symbols(self) -> SymbolsAPI:
        """Access symbols API endpoints"""
        if self._symbols is None:
            self._symbols = SymbolsAPI(self)
        return self._symbols

    @property
    def quotes(self) -> QuotesAPI:
        """Access quotes API endpoints"""
        if self._quotes is None:
            self._quotes = QuotesAPI(self)
        return self._quotes

    @property
    def corporate(self) -> CorporateAPI:
        """Access corporate API endpoints (profiles, splits, dividends)"""
        if self._corporate is None:
            self._corporate = CorporateAPI(self)
        return self._corporate

    @property
    def fundamentals(self) -> FundamentalsAPI:
        """Access fundamental data API endpoints"""
        if self._fundamentals is None:
            self._fundamentals = FundamentalsAPI(self)
        return self._fundamentals

    @property
    def technicals(self) -> TechnicalsAPI:
        """Access technical indicators API endpoints"""
        if self._technicals is None:
            self._technicals = TechnicalsAPI(self)
        return self._technicals

    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, **kwargs) -> dict:
        """
        Make HTTP request to EODData API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            JSON response data

        Raises:
            EODDataAuthError: Authentication failed
            EODDataAPIError: API returned an error
            EODDataError: General error occurred
        """
        # Extract operation ID from endpoint for accounting purposes
        operation_id = "unknown"
        if endpoint:
            # Try to extract operation from endpoint path
            parts = endpoint.strip('/').split('/')
            if len(parts) >= 2:
                operation_id = f"{parts[1]}_{parts[0] if parts[0] != 'api' else 'unknown'}"
            elif len(parts) >= 1:
                operation_id = parts[0]
        
        # Increment accounting counter if tracking is enabled
        if self.accounting:
            try:
                self.accounting.increment_call(self.api_key, operation_id)
                # Check quotas if enabled
                self.accounting.check_quota(self.api_key, operation_id)
            except Exception as e:
                # If quota exceeded or other accounting error, re-raise but continue with request
                if not isinstance(e, Exception):
                    # Re-raise the accounting error if it's a quota violation
                    raise e

        url = f"{self.base_url}{endpoint}"

        # Add API key to params
        if params is None:
            params = {}
        if 'ApiKey' not in params and self.api_key:
            params['ApiKey'] = self.api_key

        # Log request details in debug mode
        if self.debug:
            # Mask API key for security
            debug_params = params.copy() if params else {}
            if 'ApiKey' in debug_params:
                debug_params['ApiKey'] = '***MASKED***'

            self.logger.debug(f"Making {method} request to: {url}")
            self.logger.debug(f"Request parameters: {debug_params}")
            self.logger.debug(f"Request headers: {dict(self._session.headers)}")

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.timeout,
                **kwargs
            )

            # Log response details in debug mode
            if self.debug:
                content_length = len(response.content) if response.content else 0
                self.logger.debug(f"Response status code: {response.status_code}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                self.logger.debug(f"Response content length: {content_length} bytes")
                if response.status_code != 200:
                    self.logger.debug(f"Response content preview: {response.text[:500]}...")

            # Handle different status codes
            if response.status_code == 401:
                raise EODDataAuthError("Authentication failed. Check your API key.")
            elif response.status_code == 404:
                raise EODDataAPIError(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                raise EODDataAPIError("Rate limit exceeded. Please wait before making more requests.")
            elif not response.ok:
                raise EODDataAPIError(f"API request failed with status {response.status_code}: {response.text}")

            # Parse JSON response
            try:
                return response.json()
            except ValueError:
                raise EODDataError(f"Invalid JSON response: {response.text}")

        except requests.exceptions.Timeout:
            raise EODDataError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise EODDataError("Connection error. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise EODDataError(f"Request failed: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
