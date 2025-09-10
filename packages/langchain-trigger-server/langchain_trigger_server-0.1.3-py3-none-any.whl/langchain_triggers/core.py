"""Core types and interfaces for the triggers framework."""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field



class ProviderAuthInfo(BaseModel):
    """Authentication info for a specific OAuth provider."""
    
    token: Optional[str] = None
    auth_required: bool = False
    auth_url: Optional[str] = None
    auth_id: Optional[str] = None


class UserAuthInfo(BaseModel):
    """User authentication info containing OAuth tokens or auth requirements."""
    
    user_id: str
    providers: Dict[str, ProviderAuthInfo] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class MetadataManager:
    """Manages trigger registration metadata with database persistence."""
    
    def __init__(self, database: Any, registration_id: str, initial_metadata: Dict[str, Any]):
        self.database = database
        self.registration_id = registration_id
        self.metadata = initial_metadata.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a metadata value by key."""
        return self.metadata.get(key, default)
    
    async def update(self, updates: Dict[str, Any]) -> None:
        """Update metadata and persist to database."""
        # Update local state
        self.metadata.update(updates)
        
        # Persist to database
        await self.database.update_trigger_metadata(self.registration_id, updates)



class AgentInvocationRequest(BaseModel):
    """Request to invoke an AI agent."""
    
    assistant_id: str
    user_id: str
    input_data: Any
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TriggerHandlerResult(BaseModel):
    """Result returned by trigger handlers."""
    
    invoke_agent: bool = Field(default=True, description="Whether to invoke agents for this event")
    data: Optional[str] = Field(default=None, description="String data to send to agents")
    
    def model_post_init(self, __context) -> None:
        """Validate that data is provided when invoke_agent is True."""
        if self.invoke_agent and not self.data:
            raise ValueError("data field is required when invoke_agent is True")


class TriggerRegistrationResult(BaseModel):
    """Result returned by registration handlers."""
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata to store with the registration")


class TriggerRegistrationModel(BaseModel):
    """Base class for trigger resource models that define how webhooks are matched to registrations."""
    
    class Config:
        arbitrary_types_allowed = True