## Langgraph Guard

This package is required for integrating your Langchain based Agentic Application to Aryaka's AISecure Guard Service.

## What it does

`langgraph-guard` adds a security validation layer to any LangGraph app. It intercepts user inputs, LLM prompts and responses, tool I/O, retriever I/O, and final outputs via a LangGraph callback handler and synchronously calls your AISecure GenAI Protect service to validate content. If the service returns a non-pass verdict, execution is blocked (raises `RuntimeError`).

Validation is policy-driven: the guard chooses an inspection object (inspect name) based on the current user identity, groups, workflow stage, and hook. You provide this mapping using environment variables so no application code changes are needed.

## Configuration (via environment variables)

All configuration is loaded from environment variables (e.g., from a `.env` file). At minimum, enable the guard and provide the service URL, default inspection object, stage mapping, and tenant/site identifiers.

Required when `GUARD_ENABLED=true`:
- `GUARD_URL`: Base URL of the AI Secure Validation API. 
- `GUARD_DEFAULT_INSPECT`: Fallback inspection object name.
- `GUARD_STAGE_MAP`: JSON mapping that selects inspection objects by stage/group/user/hook.
- `GUARD_CUSTOMER_ID`: Customer ID
- `GUARD_TENANT_ID`: Tenant ID.
- `GUARD_SITE_ID`: Site ID.
- TLS either:
  - `GUARD_INSECURE_SKIP_VERIFY=true` (dev only), or
  - both `GUARD_CA_PATH` and `GUARD_CA_PEM` set for certificate verification.

Optional:
- `GUARD_JWT`: Bearer token for the guard service.
- `GUARD_USER_ID`: Default user id (if not provided at runtime).
- `GUARD_GROUPS`: JSON array of groups for policy resolution (e.g., `["analysts","admins"]`).

Example `.env` snippet:

```bash
GUARD_ENABLED=true
GUARD_URL=https://protect.example.com
GUARD_JWT=eyJhbGciOiJI... # optional
GUARD_DEFAULT_INSPECT=inspect_default
GUARD_STAGE_MAP={
  "stage:plan": {"pre_llm": "inspect_plan"},
  "group:analysts": {"pre_llm": "inspect_group"},
  "user:alice": {"final_output": "inspect_user"},
  "*": {"final_output": "inspect_default"}
}
GUARD_CUSTOMER_ID=ciid-123
GUARD_TENANT_ID=tenant-abc
GUARD_SITE_ID=site-001
# One of the following TLS setups
GUARD_INSECURE_SKIP_VERIFY=false
GUARD_CA_PATH=/etc/ssl/certs/ca-bundle.crt
GUARD_CA_PEM="-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n"
```

`GUARD_STAGE_MAP` shape (keys → hook → inspect name):
- Keys may be:
  - `stage:<name>` or just `<name>` for a workflow stage
  - `group:<name>` for group-based rule
  - `user:<id>` for user-specific rule
  - `*` wildcard for any stage
- Hooks supported by the handler:
  - `user_input`, `final_output`, `pre_llm`, `post_llm`, `pre_tool`, `post_tool`, `pre_mcp`, `post_mcp`, `error`

## How to use

You can attach the guard with zero code changes using environment variables, or explicitly in code.

### 1) Environment-driven (no code changes)
Wrap your LangGraph runnable factory with the provided decorator. The guard will read all settings from env and attach itself only if `GUARD_ENABLED=true` and required vars are present.

```python
from langgraph_guard import guard

@guard
def get_app():
    # build and return your LangGraph runnable
    return app
```

Alternatively, if you already have an `app` instance:

```python
from langgraph_guard import attach_guard_from_env

app = attach_guard_from_env(app)
```

### 2) Programmatic attach (custom config objects)
If you centralize config in your app, you can pass that object to attach based on its attributes:

```python
from langgraph_guard import attach_guard_if_enabled

class AppConfig:
    guard_enabled = True
    guard_url = "https://protect.example.com"
    guard_jwt = "..."  # optional
    guard_default_inspect = "inspect_default"
    guard_customer_id = "ciid-123"
    guard_tenant_id = "tenant-abc"
    guard_site_id = "site-001"
    guard_ca_path = "/etc/ssl/certs/ca-bundle.crt"
    guard_ca_pem = None
    guard_insecure_skip_verify = False
    # Optional identity defaults
    guard_user_id = "anonymous"
    guard_groups = ["analysts"]

# Ensure GUARD_STAGE_MAP is provided via environment
app = attach_guard_if_enabled(app, AppConfig())
```
