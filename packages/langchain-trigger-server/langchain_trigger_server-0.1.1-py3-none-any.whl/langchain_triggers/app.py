"""FastAPI application for trigger server."""

from __future__ import annotations

import logging
import os
from typing import Any, Callable, Dict, List, Optional

import httpx

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .core import UserAuthInfo, ProviderAuthInfo, MetadataManager
from .decorators import TriggerTemplate
from .database import create_database, TriggerDatabaseInterface

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication for API endpoints."""
    
    def __init__(self, app, auth_handler: Callable):
        super().__init__(app)
        self.auth_handler = auth_handler
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for webhooks, health/root endpoints, and OPTIONS requests
        if (request.url.path.startswith("/webhooks/") or 
            request.url.path in ["/", "/health"] or
            request.method == "OPTIONS"):
            return await call_next(request)
        
        try:
            # Run mandatory custom authentication
            identity = await self.auth_handler({}, dict(request.headers))
            
            if not identity or not identity.get("identity"):
                return Response(
                    content='{"detail": "Authentication required"}',
                    status_code=401,
                    media_type="application/json"
                )
            
            # Store identity in request state for endpoints to access
            request.state.current_user = identity
            
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            return Response(
                content='{"detail": "Authentication failed"}',
                status_code=401,
                media_type="application/json"
            )
        
        return await call_next(request)


def get_current_user(request: Request) -> Dict[str, Any]:
    """FastAPI dependency to get the current authenticated user."""
    if not hasattr(request.state, "current_user"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return request.state.current_user


class TriggerServer:
    """FastAPI application for trigger webhooks."""
    
    def __init__(
        self,
        auth_handler: Callable,
        cors_origins: Optional[List[str]] = None,
        database: Optional[TriggerDatabaseInterface] = None,
    ):
        self.app = FastAPI(
            title="Triggers Server",
            description="Event-driven triggers framework",
            version="0.1.0"
        )
        
        self.database = database or create_database()  # Default to Supabase
        self.auth_handler = auth_handler
        
        # LangGraph configuration
        self.langgraph_api_url = os.getenv("LANGGRAPH_API_URL")
        self.langgraph_api_key = os.getenv("LANGCHAIN_API_KEY")
        
        if not self.langgraph_api_url:
            raise ValueError("LANGGRAPH_API_URL environment variable is required")
        
        self.langgraph_api_url = self.langgraph_api_url.rstrip("/")

        self.langchain_auth_client = None
        try:
            from langchain_auth import Client
            langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
            if langchain_api_key:
                self.langchain_auth_client = Client(api_key=langchain_api_key)
                logger.info("Initialized LangChain Auth client for OAuth token injection")
            else:
                logger.warning("LANGCHAIN_API_KEY not found - OAuth token injection disabled")
        except ImportError:
            logger.warning("langchain_auth not installed - OAuth token injection disabled")
        
        self.triggers: List[TriggerTemplate] = []
        
        # Setup CORS
        if cors_origins is None:
            cors_origins = ["*"]  # Allow all origins by default
            
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup authentication middleware
        self.app.add_middleware(AuthenticationMiddleware, auth_handler=auth_handler)
        
        # Setup routes
        self._setup_routes()
        
        # Add startup event to ensure trigger templates exist in database
        @self.app.on_event("startup")
        async def startup_event():
            await self.ensure_trigger_templates()
    
    def add_trigger(self, trigger: TriggerTemplate) -> None:
        """Add a trigger template to the app."""
        # Check for duplicate IDs
        if any(t.id == trigger.id for t in self.triggers):
            raise ValueError(f"Trigger with id '{trigger.id}' already exists")
        
        self.triggers.append(trigger)

        if trigger.trigger_handler:
            async def handler_endpoint(request: Request) -> Dict[str, Any]:
                return await self._handle_request(trigger, request)
            
            handler_path = f"/webhooks/{trigger.id}"
            self.app.post(handler_path)(handler_endpoint)
            logger.info(f"Added handler route: POST {handler_path}")
        
        logger.info(f"Registered trigger template in memory: {trigger.name} ({trigger.id})")
    
    async def ensure_trigger_templates(self) -> None:
        """Ensure all registered trigger templates exist in the database."""
        for trigger in self.triggers:
            existing = await self.database.get_trigger_template(trigger.id)
            if not existing:
                logger.info(f"Creating new trigger template in database: {trigger.name} ({trigger.id})")
                await self.database.create_trigger_template(
                    id=trigger.id,
                    name=trigger.name,
                    description=trigger.description,
                    registration_schema=trigger.registration_model.model_json_schema()
                )
                logger.info(f"✓ Successfully created trigger template: {trigger.name} ({trigger.id})")
            else:
                logger.info(f"✓ Trigger template already exists in database: {trigger.name} ({trigger.id})")
    
    def add_triggers(self, triggers: List[TriggerTemplate]) -> None:
        """Add multiple triggers."""
        for trigger in triggers:
            self.add_trigger(trigger)
    
    def _setup_routes(self) -> None:
        """Setup built-in API routes."""
        
        @self.app.get("/")
        async def root() -> Dict[str, str]:
            return {"message": "Triggers Server", "version": "0.1.0"}
        
        @self.app.get("/health")
        async def health() -> Dict[str, str]:
            return {"status": "healthy"}
        
        @self.app.get("/api/triggers")
        async def api_list_triggers() -> Dict[str, Any]:
            """List available trigger templates."""
            templates = await self.database.get_trigger_templates()
            trigger_list = []
            for template in templates:
                trigger_list.append({
                    "id": template["id"],
                    "displayName": template["name"],
                    "description": template["description"],
                    "path": "/api/triggers/registrations",
                    "method": "POST",
                    "payloadSchema": template.get("registration_schema", {}),
                })
            
            return {
                "success": True,
                "data": trigger_list
            }
        
        @self.app.get("/api/triggers/registrations")
        async def api_list_registrations(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
            """List user's trigger registrations (user-scoped)."""
            try:
                user_id = current_user["identity"]
                
                # Get user's trigger registrations using new schema
                user_registrations = await self.database.get_user_trigger_registrations(user_id)
                
                # Format response to match expected structure
                registrations = []
                for reg in user_registrations:
                    # Get linked agent IDs
                    linked_agent_ids = await self.database.get_agents_for_trigger(reg["id"])
                    
                    registrations.append({
                        "id": reg["id"],
                        "user_id": reg["user_id"],
                        "template_id": reg.get("trigger_templates", {}).get("id"),
                        "resource": reg["resource"],
                        "linked_assistant_ids": linked_agent_ids,  # For backward compatibility
                        "created_at": reg["created_at"]
                    })
                
                return {
                    "success": True,
                    "data": registrations
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error listing registrations: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/triggers/registrations")
        async def api_create_registration(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
            """Create a new trigger registration."""
            try:
                payload = await request.json()
                logger.info(f"Registration payload received: {payload}")
                
                user_id = current_user["identity"]
                trigger_id = payload.get("type")
                if not trigger_id:
                    raise HTTPException(status_code=400, detail="Missing required field: type")
                
                trigger = next((t for t in self.triggers if t.id == trigger_id), None)
                if not trigger:
                    raise HTTPException(status_code=400, detail=f"Unknown trigger type: {trigger_id}")
                
                # Inject OAuth tokens if needed for registration
                auth_user = None
                if trigger.oauth_providers:
                    try:
                        auth_user = await self._get_authenticated_user(trigger, user_id)
                        
                        # Check if any provider requires authentication - return early if so
                        for provider in trigger.oauth_providers.keys():
                            provider_info = auth_user.providers.get(provider)
                            if provider_info and provider_info.auth_required:
                                logger.info(f"User {user_id} needs to authenticate for {provider} - returning auth URL")
                                return {
                                    "success": True,
                                    "registered": False,
                                    "auth_required": True,
                                    "auth_url": provider_info.auth_url,
                                    "auth_id": provider_info.auth_id,
                                    "provider": provider
                                }
                        
                    except Exception as e:
                        logger.error(f"OAuth authentication failed during registration: {e}")
                        raise HTTPException(status_code=500, detail="OAuth authentication failed")
                
                
                # Parse payload into registration model first
                try:
                    registration_instance = trigger.registration_model(**payload)
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid payload for trigger {trigger_type}: {str(e)}"
                    )
                
                # Call the trigger's registration handler with parsed registration model
                result = await trigger.registration_handler(registration_instance, auth_user)

                resource_dict = registration_instance.model_dump()
                registration = await self.database.create_trigger_registration(
                    user_id=user_id,
                    template_id=trigger.id,
                    resource=resource_dict,
                    metadata=result.metadata
                )
                
                if not registration:
                    raise HTTPException(status_code=500, detail="Failed to create trigger registration")
                
                # Return registration result
                return {
                    "success": True,
                    "data": registration,
                    "metadata": result.metadata
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error creating trigger registration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/triggers/registrations/{registration_id}/agents")
        async def api_list_registration_agents(registration_id: str, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
            """List agents linked to this registration."""
            try:
                user_id = current_user["identity"]
                
                # Get the specific trigger registration
                trigger = await self.database.get_user_trigger(user_id, registration_id, token)
                if not trigger:
                    raise HTTPException(status_code=404, detail="Trigger registration not found or access denied")
                
                # Return the linked agent IDs
                return {
                    "success": True,
                    "data": trigger.get("linked_assistant_ids", [])
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting registration agents: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/triggers/registrations/{registration_id}/agents/{agent_id}")
        async def api_add_agent_to_trigger(registration_id: str, agent_id: str, request: Request, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
            """Add an agent to a trigger registration."""
            try:
                # Parse request body for field selection
                try:
                    body = await request.json()
                    field_selection = body.get("field_selection")
                except:
                    field_selection = None
                
                user_id = current_user["identity"]
                
                # Verify the trigger registration exists and belongs to the user
                registration = await self.database.get_trigger_registration(registration_id, user_id)
                if not registration:
                    raise HTTPException(status_code=404, detail="Trigger registration not found or access denied")
                
                # Link the agent to the trigger
                success = await self.database.link_agent_to_trigger(
                    agent_id=agent_id,
                    registration_id=registration_id,
                    created_by=user_id,
                    field_selection=field_selection
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to link agent to trigger")
                
                return {
                    "success": True,
                    "message": f"Successfully linked agent {agent_id} to trigger {registration_id}",
                    "data": {
                        "registration_id": registration_id,
                        "agent_id": agent_id
                    }
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error linking agent to trigger: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/api/triggers/registrations/{registration_id}/agents/{agent_id}")
        async def api_remove_agent_from_trigger(registration_id: str, agent_id: str, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
            """Remove an agent from a trigger registration."""
            try:
                user_id = current_user["identity"]
                
                # Verify the trigger registration exists and belongs to the user
                registration = await self.database.get_trigger_registration(registration_id, user_id)
                if not registration:
                    raise HTTPException(status_code=404, detail="Trigger registration not found or access denied")
                
                # Unlink the agent from the trigger
                success = await self.database.unlink_agent_from_trigger(
                    agent_id=agent_id,
                    registration_id=registration_id
                )
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to unlink agent from trigger")
                
                return {
                    "success": True,
                    "message": f"Successfully unlinked agent {agent_id} from trigger {registration_id}",
                    "data": {
                        "registration_id": registration_id,
                        "agent_id": agent_id
                    }
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error unlinking agent from trigger: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/events/subscriptions")
        async def list_event_subscriptions() -> Dict[str, Any]:
            """List event bus subscriptions."""
            if hasattr(self.event_bus, "list_subscriptions"):
                subscriptions = self.event_bus.list_subscriptions()
            else:
                subscriptions = {}
            
            return {"subscriptions": subscriptions}
    
    
    async def _handle_request(
        self, 
        trigger: TriggerTemplate, 
        request: Request
    ) -> Dict[str, Any]:
        """Handle an incoming request with a handler function."""
        try:
            # Parse request data
            if request.method == "POST":
                if request.headers.get("content-type", "").startswith("application/json"):
                    payload = await request.json()
                else:
                    # Handle form data or other content types
                    body = await request.body()
                    payload = {"raw_body": body.decode("utf-8") if body else ""}
            else:
                payload = dict(request.query_params)
            
            # Step 1: Registration resolution
            if not trigger.registration_resolver:
                raise HTTPException(
                    status_code=500,
                    detail=f"Trigger {trigger.id} missing required registration_resolver"
                )
            
            # Extract resource identifiers from webhook payload
            resource_data = await trigger.registration_resolver(payload)
            
            # Find matching registration
            # Convert Pydantic model to dict for database lookup
            resource_dict = resource_data.model_dump()
            registration = await self.database.find_registration_by_resource(
                trigger.id, 
                resource_dict
            )

            if not registration:
                logger.warning(f"No registration found for trigger_id={trigger.id} with resource={resource_data}, returning 400")
                raise HTTPException(
                    status_code=400,
                    detail=f"No registration found for {trigger.id} with resource {resource_data}"
                )
            
            # Step 2: Get user_id from registration (webhooks don't use API auth)
            user_id = registration["user_id"]
            
            # Step 3: Inject OAuth tokens if needed
            auth_user = None
            if trigger.oauth_providers and self.langchain_auth_client:
                try:
                    auth_user = await self._get_authenticated_user(trigger, user_id)
                    
                    # Check if any provider requires re-authentication - this shouldn't happen in webhooks
                    for provider in trigger.oauth_providers.keys():
                        provider_info = auth_user.providers.get(provider)
                        if provider_info and provider_info.auth_required:
                            logger.error(f"User {user_id} needs to re-authenticate for {provider} - this should have been handled during registration")
                            return {
                                "success": False,
                                "error": f"Authentication required for {provider}",
                                "message": "User needs to re-authenticate this trigger"
                            }
                    
                except Exception as e:
                    logger.error(f"OAuth authentication failed: {e}")
                    # Continue without auth - triggers can handle missing tokens
            
            # Step 4: Create metadata manager
            metadata_manager = MetadataManager(
                database=self.database,
                registration_id=registration["id"],
                initial_metadata=registration.get("metadata", {})
            )
            
            # Step 5: Call handler with parsed registration data
            result = await trigger.trigger_handler(payload, auth_user, metadata_manager)
            registration_id = registration["id"]
            
            # Check if we should invoke agents
            if not result.invoke_agent:
                logger.info(f"Handler requested no agent invocation for registration {registration_id}")
                return {
                    "success": True,
                    "agents_invoked": 0
                }
            
            # Get agents linked to this trigger registration
            agent_links = await self.database.get_agents_for_trigger(registration_id)
            
            if not agent_links:
                logger.info(f"No agents linked to registration {registration_id}")
                return {
                    "success": True,
                    "agents_invoked": 0
                }
            
            logger.info(f"Processing trigger result for registration {registration_id} with {len(agent_links)} linked agents")
            
            # Invoke each linked agent
            agents_invoked = 0
            for agent_link in agent_links:
                agent_id = agent_link if isinstance(agent_link, str) else agent_link.get("agent_id")
                
                # Use the data string from TriggerHandlerResult directly
                agent_input = {
                    "messages": [
                        {"role": "human", "content": result.data}
                    ]
                }

                try:
                    await self._invoke_agent(
                        agent_id=agent_id,
                        user_id=registration["user_id"],
                        input_data=agent_input,
                    )
                    agents_invoked += 1
                except Exception as e:
                    logger.error(f"Error invoking agent {agent_id}: {e}", exc_info=True)
            
            logger.info(f"Processed trigger handler, invoked {agents_invoked} agents")
            
            return {
                "success": True,
                "agents_invoked": agents_invoked
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in trigger handler: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Trigger processing failed: {str(e)}"
            )
    
    
    async def _invoke_agent(
        self,
        agent_id: str,
        user_id: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Invoke LangGraph agent directly."""
        headers = {
            "Content-Type": "application/json",
            "x-auth-scheme": "langchain-trigger-server-event",
        }
        
        # Add API key if provided
        if self.langgraph_api_key:
            headers["Authorization"] = f"Bearer {self.langgraph_api_key}"
        
        # Add user-specific headers
        if user_id:
            headers["x-supabase-user-id"] = user_id
        
        payload = {
            "input": input_data,
            "assistant_id": agent_id,
            "metadata": {
                "triggered_by": "langchain-triggers",
                "user_id": user_id,
            },
        }
        
        # Let LangGraph create a new thread automatically
        url = f"{self.langgraph_api_url}/runs"
        
        logger.info(f"Invoking LangGraph agent {agent_id} for user {user_id}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Successfully invoked agent {agent_id}")
                return result
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error invoking agent: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error invoking agent {agent_id}: {e}")
                raise
    
    async def _get_authenticated_user(self, trigger: TriggerTemplate, user_id: str) -> UserAuthInfo:
        """Get authenticated user with OAuth tokens for the trigger's required providers."""
        providers = {}
        
        # Get tokens for each required OAuth provider
        for provider, scopes in trigger.oauth_providers.items():
            try:
                auth_result = await self.langchain_auth_client.authenticate(
                    provider=provider,
                    scopes=scopes,
                    user_id=user_id
                )
                
                # Debug logging
                logger.info(f"Auth result for {provider}: {vars(auth_result) if hasattr(auth_result, '__dict__') else 'Not available'}")
                
                if hasattr(auth_result, 'token') and auth_result.token:
                    providers[provider] = ProviderAuthInfo(token=auth_result.token)
                    logger.debug(f"Successfully got {provider} token for user {user_id}")
                elif hasattr(auth_result, 'auth_required') and auth_result.auth_required:
                    logger.info(f"User {user_id} needs to authenticate for {provider}")
                    providers[provider] = ProviderAuthInfo(
                        auth_required=True,
                        auth_url=getattr(auth_result, 'auth_url', None),
                        auth_id=getattr(auth_result, 'auth_id', None)
                    )
                else:
                    logger.warning(f"No token returned for {provider} provider")
                    
            except Exception as e:
                logger.error(f"Failed to get {provider} token: {e}")
                # Continue with other providers
        
        return UserAuthInfo(user_id=user_id, providers=providers)
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI app instance."""
        return self.app