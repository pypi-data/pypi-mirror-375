"""
exceptions.py - Custom exceptions for the Axory SDK.
"""

class AuthenticationError(Exception):
    """
    Raised when JWT authentication fails.
    Example cases:
      - Invalid or expired JWT token
      - Supabase check fails (user not found / public key mismatch)
    """
    pass


class APIError(Exception):
    """
    Raised when the Axory API returns an error response.
    Example cases:
      - Non-200 status code from https://axory.tech/analyze
      - Rate limit exceeded
      - Invalid file format
    """
    pass


class ConfigurationError(Exception):
    """
    Raised when SDK configuration is invalid.
    Example cases:
      - Missing Supabase URL or key
      - Missing JWT secret/public key
    """
    pass
