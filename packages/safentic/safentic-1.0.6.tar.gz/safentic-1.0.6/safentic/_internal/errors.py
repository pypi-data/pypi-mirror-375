class SafenticError(Exception):
    """Base class for all Safentic errors."""


class PolicyValidationError(SafenticError):
    """Raised when a policy file or rule is invalid."""


class ReferenceFileError(SafenticError):
    """Raised when a reference file is missing, unreadable, or empty."""


class EnforcementError(SafenticError):
    """Raised when enforcement fails unexpectedly."""


class VerifierError(SafenticError):
    """Raised when the LLM verifier fails unexpectedly."""


class InvalidAPIKeyError(SafenticError):
    """Raised when an API key is missing or invalid."""


class InvalidAgentInterfaceError(SafenticError):
    """Raised when the wrapped agent doesn't expose the expected interface."""
