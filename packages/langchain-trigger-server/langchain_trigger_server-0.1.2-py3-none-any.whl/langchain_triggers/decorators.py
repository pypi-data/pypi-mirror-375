"""Trigger system - templates with registration and webhook handlers."""

from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, get_type_hints
from .core import UserAuthInfo, TriggerRegistrationModel, TriggerHandlerResult, TriggerRegistrationResult, MetadataManager
from pydantic import BaseModel

class TriggerTemplate:
    """A trigger template with registration handler and main handler."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        registration_model: Type[BaseModel],

        registration_handler,
        trigger_handler,
        registration_resolver,

        oauth_providers: Optional[Dict[str, List[str]]] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.registration_model = registration_model
        self.registration_handler = registration_handler
        self.trigger_handler = trigger_handler
        self.registration_resolver = registration_resolver
        self.oauth_providers = oauth_providers or {}

        self._validate_handler_signatures()
    
    def _validate_handler_signatures(self):
        """Validate that all handler functions have the correct signatures."""
        # Expected: async def handler(registration: RegistrationModel, auth_user: UserAuthInfo) -> TriggerRegistrationResult
        self._validate_handler("registration_handler", self.registration_handler, [self.registration_model, UserAuthInfo], TriggerRegistrationResult)
        
        # Expected: async def handler(payload: Dict[str, Any], auth_user: UserAuthInfo, metadata: MetadataManager) -> TriggerHandlerResult
        self._validate_handler("trigger_handler", self.trigger_handler, [Dict[str, Any], UserAuthInfo, MetadataManager], TriggerHandlerResult)
        
        # Expected: async def resolver(payload: Dict[str, Any]) -> RegistrationModel
        self._validate_handler("registration_resolver", self.registration_resolver, [Dict[str, Any]], self.registration_model)
    
    def _validate_handler(self, handler_name: str, handler_func, expected_types: List[Type], expected_return_type: Type = None):
        """Common validation logic for all handler functions."""
        if not inspect.iscoroutinefunction(handler_func):
            raise TypeError(f"{handler_name} for trigger '{self.id}' must be async")
        
        sig = inspect.signature(handler_func)
        params = list(sig.parameters.values())
        expected_param_count = len(expected_types)
        
        if len(params) != expected_param_count:
            raise TypeError(f"{handler_name} for trigger '{self.id}' must have {expected_param_count} parameters, got {len(params)}")
        
        hints = get_type_hints(handler_func)
        param_names = list(sig.parameters.keys())
        
        # Check each parameter type if type hints are available
        for i, expected_type in enumerate(expected_types):
            if param_names[i] in hints and hints[param_names[i]] != expected_type:
                expected_name = getattr(expected_type, '__name__', str(expected_type))
                raise TypeError(f"{handler_name} for trigger '{self.id}': param {i+1} should be {expected_name}")
        
        # Check return type if expected and available
        if expected_return_type and 'return' in hints:
            actual_return_type = hints['return']
            if actual_return_type != expected_return_type:
                expected_name = getattr(expected_return_type, '__name__', str(expected_return_type))
                actual_name = getattr(actual_return_type, '__name__', str(actual_return_type))
                raise TypeError(f"{handler_name} for trigger '{self.id}': return type should be {expected_name}, got {actual_name}")