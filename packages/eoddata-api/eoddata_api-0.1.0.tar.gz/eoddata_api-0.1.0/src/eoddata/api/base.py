"""
Base class for API endpoint groups
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import EODDataClient


class BaseAPI:
    """Base class for API endpoint groups"""

    def __init__(self, client: 'EODDataClient'):
        self.client = client
