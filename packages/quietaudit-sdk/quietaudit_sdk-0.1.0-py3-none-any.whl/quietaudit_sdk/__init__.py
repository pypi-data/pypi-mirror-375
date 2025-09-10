"""
QuietAudit SDK - Immutable audit trails for AI decisions

Add blockchain-based audit logging to any AI model with 2 lines of code.
"""

from .client import QuietAuditClient
from .wrappers import wrap_model

__version__ = "0.1.0"
__all__ = ["QuietAuditClient", "wrap_model"]