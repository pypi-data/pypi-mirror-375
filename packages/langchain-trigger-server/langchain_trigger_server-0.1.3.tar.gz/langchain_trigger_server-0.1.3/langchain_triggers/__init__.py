"""LangChain Triggers Framework - Event-driven triggers for AI agents."""

from .core import UserAuthInfo, TriggerRegistrationModel, TriggerHandlerResult, TriggerRegistrationResult, MetadataManager
from .decorators import TriggerTemplate
from .app import TriggerServer

__version__ = "0.1.0"

__all__ = [
    "UserAuthInfo",
    "TriggerRegistrationModel",
    "TriggerHandlerResult",
    "TriggerRegistrationResult",
    "MetadataManager",
    "TriggerTemplate",
    "TriggerServer",
]