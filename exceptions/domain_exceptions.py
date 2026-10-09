class DomainException(Exception):
    """Base class for all domain-related exceptions."""
    pass

class PlaylistNotFoundError(DomainException):
    """Raised when a requested playlist does not exist."""
    pass

class StreamSourceError(DomainException):
    """Raised when there is an error retrieving or validating a stream source."""
    pass

class DuplicateStreamError(DomainException):
    """Raised when adding a stream that already exists in the playlist."""
    pass
