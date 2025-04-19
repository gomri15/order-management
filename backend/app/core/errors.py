# TODO: check which errors are used and remove not used

class DomainError(Exception):
    """Base class for domain-level errors."""
    pass


class NotFoundError(DomainError):
    """Raised when an entity is not found in the database."""
    pass


class TokenDecodeError(Exception):
    """Raised when there is an error decoding a JWT token."""
    pass


class NoChangeError(Exception):
    """Raised when there are no changes to update."""
    pass
