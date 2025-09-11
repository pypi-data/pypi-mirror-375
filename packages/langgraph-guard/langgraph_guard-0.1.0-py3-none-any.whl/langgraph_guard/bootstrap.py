"""Main LangGraph integration for attaching Guard callbacks to any LangGraph app.

This module exposes a small, reusable API so apps can attach the guard by simply
calling one helper or using a decorator, with all configuration provided via
environment variables (or a passed dict), avoiding edits to application code.
"""

from __future__ import annotations

from typing import Optional, Any, Dict

import json
import os

from langchain_core.runnables import Runnable

from .guard_callback_blocks_only import (
    AsyncGuardHandler,
    GuardServiceConfig,
    GuardPolicy,
    PolicyKey,
    PolicyRule,
    Identity,
)


def _load_json_env(name: str) -> Optional[Dict[str, Any]]:
    """Load a JSON object from an env var if present and valid."""
    raw = os.getenv(name)
    if not raw:
        return None
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
    except Exception:
        pass
    return None


def _get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    val = os.getenv(key)
    return val if val is not None else default


def _build_policy_from_env(stage_mapping: Optional[Dict[str, Any]], default_inspect: Optional[str]) -> GuardPolicy:
    """Create GuardPolicy from a stage->inspect mapping dict.

    Expected shape (in env var GUARD_STAGE_MAP_JSON):
    {
      "stage:plan": {"pre_llm": "inspect_plan"},
      "group:analysts": {"pre_llm": "inspect_group"},
      "user:alice": {"pre_llm": "inspect_user"},
      "*": {"final_output": "inspect_default"}
    }
    Keys may be:
      - "stage:<name>" or plain "<name>" for a stage
      - "group:<name>" for a group-based rule
      - "user:<id>" for a user-specific rule
      - "*" wildcard for any stage
    Values map hook->inspect_name.
    """
    rules: list[PolicyRule] = []
    if stage_mapping:
        for key, hooks in stage_mapping.items():
            if not isinstance(hooks, dict):
                continue
            # Determine key type: user, group, stage, wildcard
            user_id = None
            group = None
            stage = None
            if key == "*":
                pass
            elif key.startswith("user:"):
                user_id = key.split(":", 1)[1]
            elif key.startswith("group:"):
                group = key.split(":", 1)[1]
            elif key.startswith("stage:"):
                stage = key.split(":", 1)[1]
            else:
                stage = key
            for hook, inspect in hooks.items():
                if not inspect:
                    continue
                rules.append(PolicyRule(
                    key=PolicyKey(user_id=user_id, group=group, stage=stage, hook=hook),
                    inspect_name=inspect,
                ))

    return GuardPolicy(rules=rules, default_inspect_name=default_inspect)


def attach_guard_if_enabled(app: Runnable, config_values: Any) -> Runnable:
    """Attach the Guard callback globally to the runnable if enabled in config.
    
    This function sets up comprehensive guard protection for all stages of the Langchain Application workflow.
    The Guard JWT token is used for authentication with the GenAI Protect service.
    
    Args:
        app: The LangGraph runnable to protect with guard callbacks
        config_values: Configuration object containing guard settings and inspect object mappings
        
    Returns:
        The original runnable with guard callbacks attached, or unmodified if guards are disabled
    """
    # Early exit if guards are disabled in configuration
    if not getattr(config_values, "guard_enabled", False):
        return app

    # Early exit if no guard service URL is configured
    if not getattr(config_values, "guard_url", None):
        return app

    # Env-driven JSON mapping is the source of truth for stage mapping
    stage_map = _load_json_env("GUARD_STAGE_MAP")
    policy = _build_policy_from_env(stage_map, getattr(config_values, "guard_default_inspect", None))
    # If no mapping and no default inspect, disable to avoid accidental pass-through
    if not policy.rules and policy.default_inspect_name is None:
        import logging
        logging.warning("Guard enabled but neither GUARD_STAGE_MAP nor GUARD_DEFAULT_INSPECT is configured. Disabling guard.")
        return app

    # Create identity for guard validation
    # The guard_jwt will be used for authentication with GenAI Protect
    identity = Identity(
        user_id=getattr(config_values, "guard_user_id", None) or _get_env("GUARD_USER_ID", "anonymous"),
        groups=getattr(config_values, "guard_groups", None) or json.loads(_get_env("GUARD_GROUPS", "[]")),
    )

    # Initialize the guard handler with service configuration
    handler = AsyncGuardHandler(
        service=GuardServiceConfig(
            service_url=(getattr(config_values, "guard_url", None) or _get_env("GUARD_URL") or ""),
            jwt=getattr(config_values, "guard_jwt", None) or _get_env("GUARD_JWT"),
            ca_cert_path=getattr(config_values, "guard_ca_path", None) or _get_env("GUARD_CA_PATH"),
            ca_cert_pem=getattr(config_values, "guard_ca_pem", None) or _get_env("GUARD_CA_PEM"),
            insecure_skip_verify=bool(getattr(config_values, "guard_insecure_skip_verify", None) or _get_env("GUARD_INSECURE_SKIP_VERIFY", "false").lower() == "true"),
        ),
        identity=identity,
        policy=policy,
        ciid=(getattr(config_values, "guard_customer_id", None) or _get_env("GUARD_CUSTOMER_ID") or ""),
        default_tsid=(getattr(config_values, "guard_tenant_id", None) or getattr(config_values, "tsid", None) or _get_env("GUARD_TENANT_ID")),
        default_sid=(getattr(config_values, "guard_site_id", None) or getattr(config_values, "sid", None) or _get_env("GUARD_SITE_ID")),
    )
    
    # Reset the root run ID tracker for this handler instance
    handler.reset_root()
    
    # Build configurable dict with tenant/site identifiers if present
    configurable = {}
    tsid = getattr(config_values, "guard_tenant_id", None) or getattr(config_values, "tsid", None) or _get_env("GUARD_TENANT_ID")
    sid = getattr(config_values, "guard_site_id", None) or getattr(config_values, "sid", None) or _get_env("GUARD_SITE_ID")
    
    if tsid:
        configurable["guard_tsid"] = tsid
    if sid:
        configurable["guard_sid"] = sid
    
    # Validate required fields when enabled
    missing: list[str] = []
    if not handler.service.service_url:
        missing.append("GUARD_URL")
    if not policy.default_inspect_name:
        missing.append("GUARD_DEFAULT_INSPECT")
    if not stage_map:
        missing.append("GUARD_STAGE_MAP")
    if not handler.ciid:
        missing.append("GUARD_CUSTOMER_ID")
    if not tsid:
        missing.append("GUARD_TENANT_ID")
    if not sid:
        missing.append("GUARD_SITE_ID")
    if not handler.service.insecure_skip_verify:
        if not (handler.service.ca_cert_path and handler.service.ca_cert_pem):
            # both required when not skipping verify
            if not handler.service.ca_cert_path:
                missing.append("GUARD_CA_PATH")
            if not handler.service.ca_cert_pem:
                missing.append("GUARD_CA_PEM")
    if missing:
        import logging
        logging.warning(f"Guard enabled but required settings are missing: {', '.join(missing)}. Disabling guard.")
        return app

    # Attach handler with configurable if present, otherwise just handler
    if configurable:
        return app.with_config({"callbacks": [handler], "configurable": configurable})
    return app.with_config({"callbacks": [handler]})


def attach_guard_from_env(app: Runnable) -> Runnable:
    """Attach guard callbacks reading all settings from environment variables.

    Required envs when GUARD_ENABLED=true:
      - GUARD_URL
      - GUARD_DEFAULT_INSPECT
      - GUARD_STAGE_MAP (JSON mapping stage/group/user/wildcard -> hook -> inspect)
      - GUARD_CUSTOMER_ID (maps to config_instance_id)
      - GUARD_TENANT_ID (maps to customer_id)
      - GUARD_SITE_ID (maps to site_id)
      - GUARD_CA_PATH and GUARD_CA_PEM (both) unless GUARD_INSECURE_SKIP_VERIFY=true
    Optional:
      - GUARD_JWT, GUARD_USER_ID, GUARD_GROUPS (JSON array)
    """
    enabled = os.getenv("GUARD_ENABLED", "false").lower() == "true"
    if not enabled:
        return app

    class _EnvCfg:
        pass

    cfg = _EnvCfg()
    cfg.guard_enabled = enabled
    cfg.guard_url = _get_env("GUARD_URL")
    cfg.guard_jwt = _get_env("GUARD_JWT")
    cfg.guard_default_inspect = _get_env("GUARD_DEFAULT_INSPECT")
    cfg.guard_user_id = _get_env("GUARD_USER_ID")
    try:
        cfg.guard_groups = json.loads(_get_env("GUARD_GROUPS", "[]"))
    except Exception:
        cfg.guard_groups = []
    cfg.guard_customer_id = _get_env("GUARD_CUSTOMER_ID")
    cfg.guard_tenant_id = _get_env("GUARD_TENANT_ID")
    cfg.guard_site_id = _get_env("GUARD_SITE_ID")
    cfg.guard_ca_path = _get_env("GUARD_CA_PATH")
    cfg.guard_ca_pem = _get_env("GUARD_CA_PEM")
    cfg.guard_insecure_skip_verify = _get_env("GUARD_INSECURE_SKIP_VERIFY", "false").lower() == "true"

    return attach_guard_if_enabled(app, cfg)


def guard(app_factory):
    """Decorator to wrap a LangGraph runnable factory and attach guard from env.

    Usage:
        @guard
        def get_app():
            return my_runnable
    """
    def _wrapper(*args, **kwargs):
        runnable = app_factory(*args, **kwargs)
        return attach_guard_from_env(runnable)
    return _wrapper


