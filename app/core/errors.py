class DomainError(Exception):
    """Base class for domain-level errors."""
    pass


class NotFoundError(DomainError):
    """Raised when an entity is not found in the database."""
    pass


class DuplicateSKUError(DomainError):
    """Raised when a SKU already exists during product creation."""
    pass


class UnauthorizedError(DomainError):
    """Raised when a user tries to access something they shouldn't."""
    pass


class TokenDecodeError(Exception):
    """Raised when there is an error decoding a JWT token."""
    pass

class NoChangeError(Exception):
    """Raised when there are no changes to update."""
    pass