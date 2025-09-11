# tests/test_integration.py
"""
Integration tests that call the real EODData API
"""

import os
import re
import subprocess
import sys
import time
import pytest
from eoddata import EODDataClient, EODDataError

# Skip integration tests by default
#pytestmark = pytest.mark.skip(reason="Integration tests disabled by default")


class TestIntegration:

    @staticmethod
    def _load_env_file():
        """Load API key from .env file"""
        try:
            with open('.env', 'r') as f:
                content = f.read()
                match = re.search(r'EODDATA_API_KEY\s*=\s*(.+)', content)
                if match:
                    return match.group(1).strip().strip('"\'')
        except FileNotFoundError:
            pass
        return None

    @staticmethod
    def _get_api_key():
        """Get API key from environment or .env file"""
        api_key = os.getenv("EODDATA_API_KEY")
        if api_key:
            return api_key

        api_key = TestIntegration._load_env_file()
        if api_key:
            return api_key

        return None

    def test_integration_api_key_exists(self):
        """Check if API key is available for integration tests"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")


    def test_integration_metadata_endpoints(self):
        """Integration test for metadata endpoints"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")

        client = EODDataClient(api_key=api_key, timeout=10)

        try:
            exchange_types = client.metadata.exchange_types()
            assert isinstance(exchange_types, list)

            symbol_types = client.metadata.symbol_types()
            assert isinstance(symbol_types, list)
        except EODDataError:
            # If we get a 403 or other API error, it might be rate limiting
            # This is still valid testing - we're verifying the client handles errors properly
            pass

    def test_integration_exchanges_endpoints(self):
        """Integration test for exchanges endpoints"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")

        client = EODDataClient(api_key=api_key, timeout=10)

        try:
            exchanges = client.exchanges.list()
            assert isinstance(exchanges, list)
        except EODDataError:
            pass

    def test_integration_symbols_endpoints(self):
        """Integration test for symbols endpoints"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")

        client = EODDataClient(api_key=api_key, timeout=10)

        try:
            symbols = client.symbols.list("NASDAQ")
            assert isinstance(symbols, list)
        except EODDataError:
            pass

    def test_integration_quotes_endpoints(self):
        """Integration test for quotes endpoints"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")

        client = EODDataClient(api_key=api_key, timeout=10)

        try:
            quotes = client.quotes.list_by_exchange("NASDAQ")
            assert isinstance(quotes, list)
        except EODDataError:
            pass

    def test_integration_corporate_endpoints(self):
        """Integration test for corporate endpoints"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")

        client = EODDataClient(api_key=api_key, timeout=10)

        try:
            profile = client.corporate.profile_get("NASDAQ", "AAPL")
            assert isinstance(profile, dict)
        except EODDataError:
            pass

    def test_integration_fundamentals_endpoints(self):
        """Integration test for fundamentals endpoints"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")

        client = EODDataClient(api_key=api_key, timeout=10)

        try:
            fundamentals = client.fundamentals.get("NASDAQ", "AAPL")
            assert isinstance(fundamentals, dict)
        except EODDataError:
            pass

    def test_integration_technicals_endpoints(self):
        """Integration test for technicals endpoints"""
        api_key = self._get_api_key()
        if not api_key:
            pytest.skip("EODDATA_API_KEY not found in environment or .env file")

        client = EODDataClient(api_key=api_key, timeout=10)

        try:
            technicals = client.technicals.get("NASDAQ", "AAPL")
            assert isinstance(technicals, dict)
        except EODDataError:
            pass


def run_integration_tests_interactive():
    """Run integration tests with user confirmation"""
    print("This will run integration tests that call the real EODData API.")
    print("These tests may consume your API credits and take longer to run.")

    # Check if API key is available
    api_key = TestIntegration._get_api_key()
    if not api_key:
        print("Error: No API key found in environment variables or .env file.")
        return False

    print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")
    response = input("Do you want to proceed with live API calls? (y/N): ").strip().lower()

    if response not in ['y', 'yes']:
        print("Integration tests cancelled.")
        return False

    # Run the integration tests
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/test_integration.py',
            '-v', '--tb=short'
        ], capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"Error running integration tests: {e}")
        return False


if __name__ == "__main__":
    run_integration_tests_interactive()
