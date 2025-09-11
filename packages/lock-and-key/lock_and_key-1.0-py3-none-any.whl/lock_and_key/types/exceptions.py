"""Base exception classes."""


class LockAndKeyError(Exception):
    """Base exception for Lock & Key."""

    pass


class ProviderError(LockAndKeyError):
    """Exception for cloud provider errors."""

    pass


class CredentialsError(LockAndKeyError):
    """Exception for credential-related errors."""

    pass
