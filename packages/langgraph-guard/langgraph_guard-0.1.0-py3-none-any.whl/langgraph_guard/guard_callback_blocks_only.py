"""AsyncGuardHandler implementation for GenAI Protect integration with LangGraph.

This module provides comprehensive security validation for all LangGraph components
through callback handlers that integrate with the GenAI Protect API service.
"""

from __future__ import annotations

import ssl
import json
import uuid as _uuid
import datetime
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, Field, HttpUrl

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult


# =============================================================================
# CONFIGURATION MODELS
# =============================================================================

class GuardServiceConfig(BaseModel):
    """Configuration for connecting to the Guard validation API service.
    
    This configuration targets the FastAPI server exposed by `api_server.py`
    and its `/v1.0/validate` endpoint for content validation.
    """
    service_url: HttpUrl
    jwt: Optional[str] = None  # Guard JWT for GenAI Protect authentication
    ca_cert_path: Optional[str] = None
    ca_cert_pem: Optional[str] = None
    timeout_s: float = 15.0
    insecure_skip_verify: bool = False


class Identity(BaseModel):
    """User identity model for policy resolution and access control."""
    user_id: str
    account_id: Optional[str] = None
    groups: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)


class PolicyKey(BaseModel):
    """Policy matching key for inspection object selection."""
    user_id: Optional[str] = None
    group: Optional[str] = None
    stage: Optional[str] = None
    hook: Optional[str] = None


class PolicyRule(BaseModel):
    """Policy rule mapping a key pattern to an inspection object."""
    key: PolicyKey
    inspect_name: str


class GuardPolicy(BaseModel):
    """Policy engine for selecting appropriate inspection objects based on context."""
    """This is not referenced."""
    rules: List[PolicyRule] = Field(default_factory=list)
    default_inspect_name: Optional[str] = None

    def resolve(self, identity: Identity, stage: Optional[str], hook: str) -> str:
        """
        Select the most specific inspection object for the current validation context.
        
        Scoring System (higher score = higher priority):
        - User ID match: +8 points (individual user override)
        - Group match: +4 points (role-based policy)
        - Stage match: +2 points (workflow-specific policy)
        - Hook match: +1 point (general hook policy)
        
        Args:
            identity: User identity with user_id, groups, etc.
            stage: Current workflow stage (application-defined string)
            hook: Current callback hook (e.g., "pre_llm", "post_tool")
            
        Returns:
            The inspect_object name to use for validation
            
        Raises:
            RuntimeError: If no inspection object can be resolved
        """
        best_inspect = None
        best_score = -1
        user_groups = set(identity.groups or [])
        
        for rule in self.rules:
            score = 0
            
            # Calculate match score for this rule
            if rule.key.user_id and rule.key.user_id == identity.user_id:
                score += 8
            if rule.key.group and rule.key.group in user_groups:
                score += 4
            if rule.key.stage and rule.key.stage == stage:
                score += 2
            if rule.key.hook and rule.key.hook == hook:
                score += 1
            
            # Track highest scoring rule
            if score > best_score:
                best_score = score
                best_inspect = rule.inspect_name
        
        if best_inspect:
            return best_inspect
        if self.default_inspect_name:
            return self.default_inspect_name
        raise RuntimeError("No inspection object could be resolved from policy")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _hook_to_validate_type(hook: str) -> str:
    """Map callback hook to validate.type expected by the guard API.
    
    The mapping determines how GenAI Protect will treat the content:
    - prompt: User inputs going to AI models
    - response: AI model outputs being returned to users
    - text: General text content for validation
    """
    mapping = {
        "user_input": "prompt",
        "pre_llm": "prompt",
        "post_llm": "response",
        "pre_tool": "text",
        "post_tool": "text",
        "pre_mcp": "text",
        "post_mcp": "text",
        "final_output": "response",
        "error": "text",
    }
    return mapping.get(hook, "text")


# =============================================================================
# ASYNC GUARD HANDLER
# =============================================================================

class AsyncGuardHandler(AsyncCallbackHandler):
    """Comprehensive Guard interceptor for security validation in LangGraph.
    
    This handler integrates with the GenAI Protect API service to validate content
    at every stage of the Langchain Application workflow. It operates in "block-only" mode,
    raising RuntimeError to halt execution when policy violations are detected.
    
    NOTE: Content is sent as stringified representations of the LangGraph objects
    because the structure varies significantly between different workflow stages.
    The GenAI Protect service will need to handle parsing these string representations.
    
    SUPPORTED CALLBACKS:
    - Chain boundaries: on_chain_start/end (user_input, final_output)
    - LLM calls: on_llm_start/end (pre_llm, post_llm)
    - Tool executions: on_tool_start/end (pre_tool, post_tool)
    - Retriever calls: on_retriever_start/end (pre_mcp, post_mcp)
    - Error handling: on_*_error callbacks
    """
    
    def __init__(self, service: GuardServiceConfig, identity: Identity,
                 policy: GuardPolicy, *, ciid: str, default_tsid: Optional[str] = None,
                 default_sid: Optional[str] = None):
        """Initialize the guard handler with configuration.
        
        Args:
            service: Guard service connection configuration (includes Guard JWT)
            identity: Static identity for policy resolution
            policy: Policy engine for inspection object selection
            ciid: Configuration Instance ID for the guard service
            default_tsid: Default tenant/customer ID
            default_sid: Default site ID
        """
        self.service = service
        self.identity = identity
        self.policy = policy
        self.ciid = ciid
        self.default_tsid = default_tsid
        self.default_sid = default_sid
        self._client: Optional[httpx.AsyncClient] = None
        self.root_run_id: Optional[str] = None
        # Cache for deduplication (key: hash of text+context, value: verdict)
        self._validation_cache: Dict[str, str] = {}
    
    def reset_root(self) -> None:
        """Reset the handler state for a new conversation."""
        self.root_run_id = None
        self._validation_cache.clear()
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Create and configure HTTP client for guard service communication."""
        verify: Union[bool, str, ssl.SSLContext] = True
        
        if self.service.insecure_skip_verify:
            verify = False
        elif self.service.ca_cert_path:
            verify = self.service.ca_cert_path
        elif self.service.ca_cert_pem:
            ctx = ssl.create_default_context()
            ctx.load_verify_locations(cadata=self.service.ca_cert_pem)
            verify = ctx
        
        headers: Dict[str, str] = {}
        if self.service.jwt:
            headers["Authorization"] = f"Bearer {self.service.jwt}"
        
        base_url = str(self.service.service_url).rstrip('/')
        return httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=self.service.timeout_s,
            verify=verify,
        )
    
    def _maybe_set_root(self, run_id: Optional[str], parent_run_id: Optional[str]) -> None:
        """Set the root run ID if not already set."""
        if not self.root_run_id and run_id:
            self.root_run_id = parent_run_id or run_id
    
    def _to_str(self, value: Any) -> str:
        """Convert any value to a string for metadata."""
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, _uuid.UUID):
            return str(value)
        try:
            return json.dumps(value, ensure_ascii=False, default=str)
        except Exception:
            return str(value)
    
    def _create_cache_key(self, text: str, inspect_name: str, stage: Optional[str], 
                         hook: str, user_id: str) -> str:
        """Create a cache key for deduplication."""
        import hashlib
        # Limit text length for cache key to avoid memory issues
        text_sample = text[:1000] if len(text) > 1000 else text
        content = f"{text_sample}|{inspect_name}|{stage or ''}|{hook}|{user_id}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    
    async def _validate(self, *, text: str, stage: Optional[str], hook: str,
                       run_id: Optional[str], parent_run_id: Optional[str],
                       tags: Optional[List[str]], metadata: Optional[Dict[str, Any]]) -> None:
        """Core validation method that sends content to the guard service.
        
        Args:
            text: The content to validate (stringified representation)
            stage: Current workflow stage
            hook: Callback hook type
            run_id: Current component execution ID
            parent_run_id: Parent component execution ID
            tags: LangGraph tags
            metadata: LangGraph metadata
            
        Raises:
            RuntimeError: If validation fails or guard service is unreachable
        """
        # DEBUG: Log all collected metadata to the same file as the payload
        if False: # Set to true for debugging purposes
            with open("api_log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().isoformat()
                f.write("=" * 80 + "\n")
                f.write(f"[{timestamp}] [DEBUG METADATA] Hook: {hook}, Stage: {stage}\n")
                f.write(f"Run ID: {run_id}\n")
                f.write(f"Parent Run ID: {parent_run_id}\n")
                f.write(f"Tags: {tags}\n")
                f.write("Raw metadata:\n")
                if metadata is None:
                    f.write("  None\n")
                else:
                    f.write(json.dumps(metadata, indent=2, default=str) + "\n")
                f.write("=" * 80 + "\n")
            
        # Skip empty content
        if not text or not text.strip():
            return
        
        # Use the configured static identity
        current_identity = self.identity
        inspect_name = self.policy.resolve(current_identity, stage, hook)
        
        # Check cache for duplicate validations
        cache_key = self._create_cache_key(text, inspect_name, stage, hook, 
                                          current_identity.user_id)
        if cache_key in self._validation_cache:
            cached_verdict = self._validation_cache[cache_key]
            if cached_verdict != "pass":
                raise RuntimeError(f"Cached validation failure: {cached_verdict}")
            return
        
        # Prepare metadata
        validate_type = _hook_to_validate_type(hook)
        raw_metadata = metadata if isinstance(metadata, dict) else {}
        
        # Build metadata with only requested fields and empty-string defaults
        meta: Dict[str, str] = {
            "hook": hook or "",
            "stage": stage or "",
            "user_id": str(raw_metadata.get("user_id") or ""),
            "thread_id": str(raw_metadata.get("thread_id") or ""),
            "assistant_id": str(raw_metadata.get("assistant_id") or ""),
            "run_id": str(run_id) if run_id else "",
            "root_run_id": str(self.root_run_id) if self.root_run_id else "",
            "parent_run_id": str(parent_run_id) if parent_run_id else "",
            "langgraph_auth_user_id": str(raw_metadata.get("langgraph_auth_user_id") or ""),
            "langgraph_request_id": str(raw_metadata.get("langgraph_request_id") or ""),
            "langgraph_node": str(raw_metadata.get("langgraph_node") or ""),
            "langgraph_step": str(raw_metadata.get("langgraph_step") or ""),
            "langgraph_checkpoint_ns": str(raw_metadata.get("langgraph_checkpoint_ns") or ""),
            "checkpoint_ns": str(raw_metadata.get("checkpoint_ns") or ""),
            "search_api": str(raw_metadata.get("search_api") or ""),
            "model": str(raw_metadata.get("model") or ""),
            "tags": ",".join([str(t) for t in tags]) if tags else "",
            "supabase_access_token": str(raw_metadata.get("supabaseAccessToken") or ""),
        }
        
        # Resolve tenant/site IDs with proper fallback chain
        tsid = (raw_metadata.get("guard_tsid") or raw_metadata.get("tsid") or 
               self.default_tsid or "default")
        sid = (raw_metadata.get("guard_sid") or raw_metadata.get("sid") or 
              self.default_sid or "default")
        
        # Build validation request payload with consistent structure
        payload = {
            "content": {
                "type": validate_type,
                "text": text,  # Stringified representation of content
            },
            "genai_protect_config": {
                "config_instance_id": self.ciid,
                "inspection_object": inspect_name,
                "customer_id": tsid,
                "site_id": sid,
            },
            "metadata": meta,
            "source": raw_metadata.get("graph_id", "") or "Langgraph Agent",
        }
        
        # Send validation request
        client = await self._get_client()
        try:
            # Debug logging (optional, can be removed in production)
            if True:  # Set to True for debugging
                with open("api_log", "a", encoding="utf-8") as f:
                    timestamp = datetime.datetime.now().isoformat()
                    f.write(f"[{timestamp}] [DEBUG] Payload: {json.dumps(payload, indent=2, default=str)}\n")
            
            # POST to /v1.0/validate endpoint
            response = await client.post("/v1.0/validate", json=payload)
            response.raise_for_status()
            
            # Parse response
            data = response.json() if response.content else {}
            verdict = str(data.get("overallverdict", "fail")).lower()
            
            # Cache the result
            self._validation_cache[cache_key] = verdict
            
            # Block if validation failed
            if verdict != "pass":
                reason = data.get("message") or "Content blocked by guard"
                raise RuntimeError(reason)
            
        finally:
            await client.aclose()
    
    # =============================================================================
    # CALLBACK IMPLEMENTATIONS
    # =============================================================================
    
    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], *,
                            run_id: str, parent_run_id: Optional[str] = None, tags=None,
                            metadata=None, **_):
        """Validate user inputs when chains start."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Convert inputs to string representation
        text = str(inputs)
        
        # Determine stage from metadata or serialized info
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage and isinstance(serialized, dict):
            stage = serialized.get("id") or serialized.get("name")
        if not stage:
            stage = "chain"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="user_input",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    async def on_chain_end(self, outputs: Dict[str, Any], *, run_id: str,
                          parent_run_id: Optional[str] = None, tags=None,
                          metadata=None, **_):
        """Validate final outputs when chains complete."""
        # Convert outputs to string representation
        text = str(outputs)
        
        # Determine stage from metadata
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage:
            stage = "chain"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="final_output",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], *,
                          run_id: str, parent_run_id: Optional[str] = None, tags=None,
                          metadata=None, **_):
        """Validate prompts before they are sent to LLM providers."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Join prompts into single string
        text = "\n\n".join(prompts or [])
        
        # Determine stage from metadata
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage:
            stage = "llm"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="pre_llm",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    async def on_llm_end(self, response: LLMResult, *, run_id: str,
                        parent_run_id: Optional[str] = None, tags=None,
                        metadata=None, **_):
        """Validate LLM responses after they are received."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Extract text from LLM response
        text_parts = []
        for generation_list in response.generations:
            for generation in generation_list:
                text_parts.append(generation.text if hasattr(generation, 'text') else str(generation))
        
        text = "\n\n".join(text_parts)
        
        # Determine stage from metadata
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage:
            stage = "llm"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="post_llm",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, *,
                           run_id: str, parent_run_id: Optional[str] = None, tags=None,
                           metadata=None, **_):
        """Validate tool inputs before execution."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Convert tool input to string
        text = str(input_str)
        
        # Determine stage from metadata
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage:
            stage = "tool"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="pre_tool",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    async def on_tool_end(self, output: str, *, run_id: str,
                         parent_run_id: Optional[str] = None, tags=None,
                         metadata=None, **_):
        """Validate tool outputs after execution."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Convert tool output to string
        text = str(output)
        
        # Determine stage from metadata
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage:
            stage = "tool"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="post_tool",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    async def on_retriever_start(self, serialized: Dict[str, Any], query: str, *,
                                run_id: str, parent_run_id: Optional[str] = None,
                                tags=None, metadata=None, **_):
        """Validate retriever queries before execution."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Query is already a string
        text = str(query)
        
        # Determine stage from metadata
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage:
            stage = "retriever"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="pre_mcp",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    async def on_retriever_end(self, documents: List[Any], *, run_id: str,
                              parent_run_id: Optional[str] = None, tags=None,
                              metadata=None, **_):
        """Validate retriever results after execution."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Extract text from retrieved documents
        text_parts = []
        for doc in (documents or []):
            if hasattr(doc, 'page_content'):
                text_parts.append(doc.page_content)
            else:
                text_parts.append(str(doc))
        
        text = "\n\n".join(text_parts)
        
        # Determine stage from metadata
        stage = None
        if isinstance(metadata, dict):
            stage = metadata.get("stage")
        if not stage:
            stage = "retriever"
        
        await self._validate(
            text=text,
            stage=stage,
            hook="post_mcp",
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata
        )
    
    # =============================================================================
    # ERROR HANDLERS (Optional - only validate long error messages)
    # =============================================================================
    
    async def on_llm_error(self, error: Exception, *, run_id: str,
                          parent_run_id: Optional[str] = None, tags=None,
                          metadata=None, **_):
        """Handle LLM errors."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Convert error to string
        text = str(error)
        
        # Only validate if error text is long enough to potentially contain sensitive data
        if len(text) > 100:
            stage = metadata.get("stage", "llm") if isinstance(metadata, dict) else "llm"
            await self._validate(
                text=text,
                stage=stage,
                hook="error",
                run_id=run_id,
                parent_run_id=parent_run_id,
                tags=tags,
                metadata=metadata
            )
    
    async def on_tool_error(self, error: Exception, *, run_id: str,
                           parent_run_id: Optional[str] = None, tags=None,
                           metadata=None, **_):
        """Handle tool errors."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Convert error to string
        text = str(error)
        
        # Only validate if error text is long enough to potentially contain sensitive data
        if len(text) > 100:
            stage = metadata.get("stage", "tool") if isinstance(metadata, dict) else "tool"
            await self._validate(
                text=text,
                stage=stage,
                hook="error",
                run_id=run_id,
                parent_run_id=parent_run_id,
                tags=tags,
                metadata=metadata
            )
    
    async def on_retriever_error(self, error: Exception, *, run_id: str,
                                parent_run_id: Optional[str] = None, tags=None,
                                metadata=None, **_):
        """Handle retriever errors."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Convert error to string
        text = str(error)
        
        # Only validate if error text is long enough to potentially contain sensitive data
        if len(text) > 100:
            stage = metadata.get("stage", "retriever") if isinstance(metadata, dict) else "retriever"
            await self._validate(
                text=text,
                stage=stage,
                hook="error",
                run_id=run_id,
                parent_run_id=parent_run_id,
                tags=tags,
                metadata=metadata
            )
    
    async def on_chain_error(self, error: Exception, *, run_id: str,
                            parent_run_id: Optional[str] = None, tags=None,
                            metadata=None, **_):
        """Handle chain errors."""
        self._maybe_set_root(run_id, parent_run_id)
        
        # Convert error to string
        text = str(error)
        
        # Only validate if error text is long enough to potentially contain sensitive data
        if len(text) > 100:
            stage = metadata.get("stage", "chain") if isinstance(metadata, dict) else "chain"
            await self._validate(
                text=text,
                stage=stage,
                hook="error",
                run_id=run_id,
                parent_run_id=parent_run_id,
                tags=tags,
                metadata=metadata
            )


