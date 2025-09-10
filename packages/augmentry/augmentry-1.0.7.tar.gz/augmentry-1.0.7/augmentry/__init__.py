"""
Augmentry Python SDK
Official Python client for the Augmentry API
"""

from .client import AugmentryClient, SyncAugmentryClient
from .exceptions import AugmentryError, AuthenticationError, RateLimitError, APIError, ValidationError

__version__ = "1.0.7"
__all__ = ["AugmentryClient", "SyncAugmentryClient", "AugmentryError", "AuthenticationError", "RateLimitError", "APIError", "ValidationError"]