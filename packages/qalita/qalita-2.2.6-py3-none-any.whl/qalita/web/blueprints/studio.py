"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import json
import yaml
import requests
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, current_app, Response
from flask import stream_with_context


bp = Blueprint("studio", __name__)


@bp.get("/")
def studio_home():
    return render_template("studio/index.html")


# ---- Config management ----


def _qalita_home():
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    try:
        return cfg.qalita_home  # type: ignore[attr-defined]
    except Exception:
        return os.path.expanduser("~/.qalita")


def _studio_config_path() -> str:
    root = _qalita_home()
    try:
        os.makedirs(root, exist_ok=True)
    except Exception:
        pass
    return os.path.join(root, ".studio")


def _qalita_home() -> str:
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    try:
        return getattr(cfg, "qalita_home")
    except Exception:
        return os.path.expanduser("~/.qalita")


def _read_qalita_conf() -> dict:
    try:
        path = os.path.join(_qalita_home(), "sources-conf.yaml")
        if not os.path.isfile(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _find_source_by_id(conf: dict, source_id: str) -> dict | None:
    try:
        items = conf.get("sources") if isinstance(conf.get("sources"), list) else []
        for s in items:
            if isinstance(s, dict) and str(s.get("id", "")) == str(source_id):
                return s
    except Exception:
        return None
    return None


def _redact_sensitive(obj: dict) -> dict:
    try:
        SENSITIVE = {"password", "secret", "token", "access_key", "secret_key", "connection_string", "credentials", "api_key"}
        def scrub(v):
            if isinstance(v, dict):
                return {k: ("***" if k.lower() in SENSITIVE else scrub(v2)) for k, v2 in v.items()}
            if isinstance(v, list):
                return [scrub(it) for it in v]
            return v
        return scrub(dict(obj)) if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _augment_prompt_with_context(prompt: str, issue_id: str | None, source_id: str | None, issue_details: dict | None = None, source_details: dict | None = None) -> str:
    base = prompt or ""
    meta_parts: list[str] = []
    if issue_id:
        meta_parts.append(f"Issue: {issue_id}")
    if source_id:
        meta_parts.append(f"Source: {source_id}")
    # Attach compact JSON of issue details if present
    if issue_details:
        try:
            snip = json.dumps(issue_details, ensure_ascii=False)[:800]
            meta_parts.append(f"IssueDetails: {snip}")
        except Exception:
            pass
    if source_details:
        try:
            red = _redact_sensitive(source_details)
            snip = json.dumps(red, ensure_ascii=False)[:800]
            meta_parts.append(f"SourceDetails: {snip}")
        except Exception:
            pass
    if not meta_parts:
        return base
    meta = "\n\n[Context]\n" + " | ".join(meta_parts) + "\n"  # lightweight hint
    return meta + base


def _studio_conv_dir() -> str:
    """Return the conversations directory, ensuring it exists."""
    root = _qalita_home()
    conv_dir = os.path.join(root, "studio_conversations")
    try:
        os.makedirs(conv_dir, exist_ok=True)
    except Exception:
        pass
    return conv_dir


def _safe_conv_id(raw: str) -> str:
    """Sanitize a conversation id to be filesystem-safe."""
    s = (raw or "").strip()
    if not s:
        s = datetime.utcnow().strftime("conv_%Y%m%d_%H%M%S")
    # allow alnum, dash, underscore only
    out = []
    for ch in s:
        if ch.isalnum() or ch in ("-", "_"):
            out.append(ch)
    s2 = "".join(out)
    return s2 or datetime.utcnow().strftime("conv_%Y%m%d_%H%M%S")


def _studio_conv_file_for(conv_id: str) -> str:
    conv_dir = _studio_conv_dir()
    safe_id = _safe_conv_id(conv_id)
    return os.path.join(conv_dir, f"{safe_id}.jsonl")


def _studio_conv_write(conv_id: str, record: dict) -> None:
    """Append one JSONL record to the studio conversations log.

    Errors are swallowed to avoid impacting the main request flow.
    """
    try:
        path = _studio_conv_file_for(conv_id)
        record = dict(record or {})
        if "ts" not in record:
            record["ts"] = datetime.utcnow().isoformat() + "Z"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False))
            f.write("\n")
    except Exception:
        pass


@bp.get("/conversations")
def conversations_list():
    """List available conversations (one file per conversation)."""
    conv_dir = _studio_conv_dir()
    items: list[dict] = []
    try:
        for name in os.listdir(conv_dir):
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(conv_dir, name)
            try:
                st = os.stat(path)
                # count lines may be expensive, do bounded scan
                count = 0
                with open(path, "r", encoding="utf-8") as f:
                    for _ in f:
                        count += 1
                        if count > 10000:
                            break
                items.append(
                    {
                        "id": name[:-6],
                        "file": name,
                        "size": st.st_size,
                        "mtime": datetime.utcfromtimestamp(st.st_mtime).isoformat()
                        + "Z",
                        "lines": count,
                    }
                )
            except Exception:
                continue
        # Sort by mtime desc
        items.sort(key=lambda x: x.get("mtime", ""), reverse=True)
    except Exception:
        items = []
    return jsonify({"ok": True, "items": items})


@bp.get("/conversation")
def conversation_get():
    """Return a conversation's messages from its id."""
    conv_id = _safe_conv_id(request.args.get("id", ""))
    if not conv_id:
        return jsonify({"ok": False, "message": "Missing id"}), 400
    path = _studio_conv_file_for(conv_id)
    if not os.path.isfile(path):
        return jsonify({"ok": False, "message": "Not found"}), 404
    messages: list[dict] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = (raw or "").strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                # New format uses role/text
                if isinstance(obj, dict) and obj.get("role") and obj.get("text") is not None:
                    messages.append(
                        {
                            "role": obj.get("role"),
                            "text": obj.get("text"),
                            "ts": obj.get("ts"),
                        }
                    )
                # Back-compat: prompt/response record
                elif isinstance(obj, dict) and obj.get("prompt") is not None:
                    messages.append({"role": "user", "text": obj.get("prompt"), "ts": obj.get("ts")})
                    if obj.get("response") is not None:
                        messages.append(
                            {"role": "assistant", "text": obj.get("response"), "ts": obj.get("ts")}
                        )
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc)}), 500
    return jsonify({"ok": True, "id": conv_id, "messages": messages})


@bp.get("/status")
def studio_status():
    p = _studio_config_path()
    exists = os.path.isfile(p)
    data: dict | None = None
    if exists:
        try:
            with open(p, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if raw:
                    data = json.loads(raw)
        except Exception:
            data = None
    # Surface current provider quickly for the UI
    current_provider = None
    if isinstance(data, dict):
        current_provider = data.get("current_provider")
        if not current_provider and isinstance(data.get("providers"), dict):
            # Pick one deterministically for display
            try:
                current_provider = next(iter(data["providers"].keys()))
            except Exception:
                current_provider = None
    return jsonify(
        {"configured": exists, "config": data, "current_provider": current_provider}
    )


@bp.post("/config")
def studio_save_config():
    payload = request.get_json(silent=True) or {}
    p = _studio_config_path()
    # Merge semantics to support multiple providers while remaining backward compatible
    try:
        current: dict = {}
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as rf:
                    raw = (rf.read() or "").strip()
                if raw:
                    current = json.loads(raw)
                    if not isinstance(current, dict):
                        current = {}
            except Exception:
                current = {}
        # Normalize base structure
        if "providers" not in current or not isinstance(current.get("providers"), dict):
            current["providers"] = {}
        providers: dict = current["providers"]  # type: ignore[assignment]
        # Path A: structured provider update
        provider = (payload.get("provider") or "").strip()
        conf = (
            payload.get("config") if isinstance(payload.get("config"), dict) else None
        )
        set_current = bool(payload.get("set_current"))
        if provider and conf is not None:
            providers[provider] = conf
            if set_current:
                current["current_provider"] = provider
        else:
            # Path B: legacy flat payload (e.g., { "model": "gpt-oss:20b" })
            # Interpret as local provider settings
            if "model" in payload and isinstance(payload.get("model"), str):
                local_conf = (
                    providers.get("local", {})
                    if isinstance(providers.get("local"), dict)
                    else {}
                )
                local_conf["model"] = (payload.get("model") or "").strip()
                providers["local"] = local_conf
                # Prefer local as current if not already chosen
                if not current.get("current_provider"):
                    current["current_provider"] = "local"
            else:
                # Fallback: overwrite with provided payload (explicit user intent)
                current = payload
                if "providers" not in current:
                    current = {
                        "providers": {"legacy": payload},
                        "current_provider": current.get("current_provider", "legacy"),
                    }
        # Persist
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(current, ensure_ascii=False, indent=2))
        return jsonify({"ok": True, "saved": True})
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc)}), 500


@bp.get("/check-ollama")
def check_ollama():
    url = "http://127.0.0.1:11434/api/tags"
    try:
        r = requests.get(url, timeout=2)
        ok = r.status_code == 200
        return jsonify({"ok": ok})
    except Exception:
        return jsonify({"ok": False})


@bp.get("/providers")
def list_providers():
    """Return available agent provider types and current selection from .studio config."""
    p = _studio_config_path()
    data: dict = {}
    try:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                raw = (f.read() or "").strip()
            if raw:
                data = json.loads(raw)
            if not isinstance(data, dict):
                data = {}
    except Exception:
        data = {}
    providers = data.get("providers") if isinstance(data.get("providers"), dict) else {}
    current = (
        data.get("current_provider")
        if isinstance(data.get("current_provider"), str)
        else None
    )
    # Static list for now; can be extended later or discovered dynamically
    available = [
        {"id": "local", "name": "Local Agent", "logo": "/static/ollama.png"},
        {"id": "openai", "name": "ChatGPT", "logo": "/static/chatgpt.svg"},
        {"id": "mistral", "name": "Mistral", "logo": "/static/mistral.svg"},
        {"id": "claude", "name": "Claude", "logo": "/static/sources-logos/api.svg"},
        {"id": "gemini", "name": "Gemini", "logo": "/static/sources-logos/api.svg"},
    ]
    return jsonify(
        {
            "available": available,
            "current": current,
            "configs": providers,
        }
    )


@bp.post("/check-remote")
def check_remote():
    """Best-effort connectivity check for remote AI providers (OpenAI, Mistral).

    Body: { "provider": "openai"|"mistral", "api_key": "...", "model": "..." }
    Returns: { ok: bool, message?: str, provider: str }
    """
    data = request.get_json(silent=True) or {}
    provider = (data.get("provider") or "").strip().lower()
    api_key = (data.get("api_key") or "").strip()
    model = (data.get("model") or "").strip()
    if not provider or not api_key:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "Missing provider or API key",
                    "provider": provider,
                }
            ),
            400,
        )
    try:
        if provider == "openai":
            # Lightweight models list call
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            r = requests.get(url, headers=headers, timeout=8)
            if 200 <= r.status_code < 300:
                return jsonify({"ok": True, "provider": provider})
            try:
                body = r.json()
            except Exception:
                body = {"detail": r.text[:200]}
            return (
                jsonify(
                    {
                        "ok": False,
                        "provider": provider,
                        "status": r.status_code,
                        "error": body,
                    }
                ),
                200,
            )
        if provider == "mistral":
            # Mistral whoami endpoint
            url = "https://api.mistral.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            r = requests.get(url, headers=headers, timeout=8)
            if 200 <= r.status_code < 300:
                return jsonify({"ok": True, "provider": provider})
            try:
                body = r.json()
            except Exception:
                body = {"detail": r.text[:200]}
            return (
                jsonify(
                    {
                        "ok": False,
                        "provider": provider,
                        "status": r.status_code,
                        "error": body,
                    }
                ),
                200,
            )
        if provider == "claude":
            # Anthropic models list requires API key header and version header
            url = "https://api.anthropic.com/v1/models"
            headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01"}
            r = requests.get(url, headers=headers, timeout=8)
            if 200 <= r.status_code < 300:
                return jsonify({"ok": True, "provider": provider})
            try:
                body = r.json()
            except Exception:
                body = {"detail": r.text[:200]}
            return (
                jsonify(
                    {
                        "ok": False,
                        "provider": provider,
                        "status": r.status_code,
                        "error": body,
                    }
                ),
                200,
            )
        if provider == "gemini":
            # Google Generative Language API models list with key in query
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            r = requests.get(url, timeout=8)
            if 200 <= r.status_code < 300:
                return jsonify({"ok": True, "provider": provider})
            try:
                body = r.json()
            except Exception:
                body = {"detail": r.text[:200]}
            return (
                jsonify(
                    {
                        "ok": False,
                        "provider": provider,
                        "status": r.status_code,
                        "error": body,
                    }
                ),
                200,
            )
        return (
            jsonify(
                {"ok": False, "message": "Unsupported provider", "provider": provider}
            ),
            400,
        )
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc), "provider": provider}), 200


@bp.get("/check-backend")
def check_backend():
    """Proxy healthcheck against the remote backend URL from current context.
    Avoids CORS issues in the browser and standardizes the response shape.
    """
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    backend_url: str | None = None
    token_value: str | None = None
    try:
        backend_url = getattr(cfg, "url", None)
        token_value = getattr(cfg, "token", None)
    except Exception:
        backend_url = None
        token_value = None
    # Fallback: read selected env pointer and parse URL from env file
    try:
        if not backend_url:
            home = _qalita_home()
            pointer = os.path.join(home, ".current_env")
            if os.path.isfile(pointer):
                with open(pointer, "r", encoding="utf-8") as f:
                    env_path = (f.read() or "").strip()
                if env_path and os.path.isfile(env_path):
                    with open(env_path, "r", encoding="utf-8") as ef:
                        for raw in ef.readlines():
                            line = (raw or "").strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = (k or "").strip().upper()
                            v = (v or "").strip().strip('"').strip("'")
                            if k in (
                                "QALITA_AGENT_ENDPOINT",
                                "AGENT_ENDPOINT",
                                "QALITA_URL",
                                "URL",
                            ):
                                backend_url = v
                            if (
                                k in ("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN")
                                and not token_value
                            ):
                                token_value = v
                        # no break: we want to scan whole file to capture both url and token
    except Exception:
        pass
    # Compute readiness flags
    endpoint_present = bool(backend_url)
    token_present = bool(token_value)
    configured = endpoint_present and token_present
    if not backend_url:
        return (
            jsonify(
                {
                    "ok": False,
                    "status": None,
                    "url": None,
                    "endpoint_present": endpoint_present,
                    "token_present": token_present,
                    "configured": configured,
                }
            ),
            200,
        )
    try:
        url = str(backend_url).rstrip("/") + "/api/v1/healthcheck"
    except Exception:
        url = str(backend_url) + "/api/v1/healthcheck"
    try:
        r = requests.get(url, timeout=3)
        ok = 200 <= r.status_code < 300
        return jsonify(
            {
                "ok": ok,
                "status": r.status_code,
                "url": str(backend_url).rstrip("/"),
                "endpoint_present": endpoint_present,
                "token_present": token_present,
                "configured": configured,
            }
        )
    except Exception:
        return (
            jsonify(
                {
                    "ok": False,
                    "status": None,
                    "url": str(backend_url).rstrip("/"),
                    "endpoint_present": endpoint_present,
                    "token_present": token_present,
                    "configured": configured,
                }
            ),
            200,
        )


@bp.get("/projects")
def studio_projects():
    """Proxy projects list against the remote backend URL from current context.
    Standardizes response to { ok: bool, items: [...] } and avoids CORS.
    """
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    backend_url: str | None = None
    token_value: str | None = None
    try:
        backend_url = getattr(cfg, "url", None)
        token_value = getattr(cfg, "token", None)
    except Exception:
        backend_url = None
        token_value = None
    # Fallback to env file like in check_backend
    try:
        if not backend_url:
            home = _qalita_home()
            pointer = os.path.join(home, ".current_env")
            if os.path.isfile(pointer):
                with open(pointer, "r", encoding="utf-8") as f:
                    env_path = (f.read() or "").strip()
                if env_path and os.path.isfile(env_path):
                    with open(env_path, "r", encoding="utf-8") as ef:
                        for raw in ef.readlines():
                            line = (raw or "").strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = (k or "").strip().upper()
                            v = (v or "").strip().strip('"').strip("'")
                            if k in (
                                "QALITA_AGENT_ENDPOINT",
                                "AGENT_ENDPOINT",
                                "QALITA_URL",
                                "URL",
                            ):
                                backend_url = v
                            if (
                                k in ("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN")
                                and not token_value
                            ):
                                token_value = v
    except Exception:
        pass
    if not backend_url:
        return jsonify({"ok": False, "items": [], "message": "Missing backend URL"}), 200
    try:
        url = str(backend_url).rstrip("/") + "/api/v2/projects"
    except Exception:
        url = str(backend_url) + "/api/v2/projects"
    headers = {"Accept": "application/json"}
    if token_value:
        headers["Authorization"] = f"Bearer {token_value}"
    try:
        r = requests.get(url, headers=headers, timeout=8)
        # Normalize response shapes
        try:
            body = r.json()
        except Exception:
            body = None
        def _normalize_projects(j):
            try:
                if not j:
                    return []
                if isinstance(j, list):
                    return j
                if isinstance(j, dict):
                    if isinstance(j.get("items"), list):
                        return j["items"]
                    if isinstance(j.get("data"), list):
                        return j["data"]
                    if isinstance(j.get("results"), list):
                        return j["results"]
                    if isinstance(j.get("projects"), list):
                        return j["projects"]
                    if isinstance(j.get("data"), dict) and isinstance(j["data"].get("items"), list):
                        return j["data"]["items"]
                    # Single object
                    if (j.get("id") is not None) or (j.get("name") is not None):
                        return [j]
            except Exception:
                return []
            return []
        if 200 <= r.status_code < 300:
            items = _normalize_projects(body)
            return jsonify({"ok": True, "items": items})
        # Error passthrough (without failing the request status)
        return jsonify({"ok": False, "status": r.status_code, "error": body}), 200
    except Exception as exc:
        return jsonify({"ok": False, "items": [], "message": str(exc)}), 200


@bp.get("/sources")
def studio_sources():
    """Proxy sources list against the remote backend URL from current context.
    Enrich with local presence and validation flags from ~/.qalita/sources-conf.yaml.
    Response shape: { ok: bool, items: [ { ..., local_present, local_validate } ] }
    Optional query passthrough: project_id
    """
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    backend_url: str | None = None
    token_value: str | None = None
    try:
        backend_url = getattr(cfg, "url", None)
        token_value = getattr(cfg, "token", None)
    except Exception:
        backend_url = None
        token_value = None
    # Fallback to env file like in check_backend
    try:
        if not backend_url:
            home = _qalita_home()
            pointer = os.path.join(home, ".current_env")
            if os.path.isfile(pointer):
                with open(pointer, "r", encoding="utf-8") as f:
                    env_path = (f.read() or "").strip()
                if env_path and os.path.isfile(env_path):
                    with open(env_path, "r", encoding="utf-8") as ef:
                        for raw in ef.readlines():
                            line = (raw or "").strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = (k or "").strip().upper()
                            v = (v or "").strip().strip('"').strip("'")
                            if k in (
                                "QALITA_AGENT_ENDPOINT",
                                "AGENT_ENDPOINT",
                                "QALITA_URL",
                                "URL",
                            ):
                                backend_url = v
                            if (
                                k in ("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN")
                                and not token_value
                            ):
                                token_value = v
    except Exception:
        pass
    if not backend_url:
        return jsonify({"ok": False, "items": [], "message": "Missing backend URL"}), 200
    try:
        base = str(backend_url).rstrip("/") + "/api/v2/sources"
    except Exception:
        base = str(backend_url) + "/api/v2/sources"
    # Optional filters passthrough
    params = {}
    project_id = (request.args.get("project_id") or "").strip()
    if project_id:
        params["project_id"] = project_id
    headers = {"Accept": "application/json"}
    if token_value:
        headers["Authorization"] = f"Bearer {token_value}"
    try:
        r = requests.get(base, headers=headers, params=params, timeout=8)
        try:
            body = r.json()
        except Exception:
            body = None
        def _normalize_sources(j):
            try:
                if not j:
                    return []
                if isinstance(j, list):
                    return j
                if isinstance(j, dict):
                    if isinstance(j.get("items"), list):
                        return j["items"]
                    if isinstance(j.get("data"), list):
                        return j["data"]
                    if isinstance(j.get("results"), list):
                        return j["results"]
                    if isinstance(j.get("data"), dict) and isinstance(j["data"].get("items"), list):
                        return j["data"]["items"]
                    if isinstance(j.get("sources"), list):
                        return j["sources"]
                    # Single object
                    if (j.get("id") is not None) or (j.get("name") is not None):
                        return [j]
            except Exception:
                return []
            return []
        if 200 <= r.status_code < 300:
            items = _normalize_sources(body)
            # Enrich with local conf presence and validate flag
            conf = _read_qalita_conf()
            local_sources = conf.get("sources") if isinstance(conf.get("sources"), list) else []
            local_by_id: dict[str, dict] = {}
            try:
                for s in local_sources:
                    if isinstance(s, dict) and s.get("id") is not None:
                        local_by_id[str(s.get("id"))] = s
            except Exception:
                local_by_id = {}
            enriched = []
            seen_ids: set[str] = set()
            for it in items:
                try:
                    obj = dict(it) if isinstance(it, dict) else {"value": it}
                except Exception:
                    obj = {"value": it}
                sid = str(obj.get("id", ""))
                if sid:
                    seen_ids.add(sid)
                lobj = local_by_id.get(sid)
                obj["local_present"] = bool(lobj is not None)
                if isinstance(lobj, dict):
                    val = lobj.get("validate")
                    try:
                        obj["local_validate"] = (str(val).lower() if val is not None else None)
                    except Exception:
                        obj["local_validate"] = None
                else:
                    obj["local_validate"] = None
                enriched.append(obj)
            # Add local-only sources (not present in backend response)
            try:
                for sid, lobj in local_by_id.items():
                    if sid in seen_ids:
                        continue
                    try:
                        name = lobj.get("name") or (
                            lobj.get("source", {}).get("name") if isinstance(lobj.get("source"), dict) else None
                        ) or f"Source {sid}"
                        stype = lobj.get("type") or (
                            lobj.get("source", {}).get("type") if isinstance(lobj.get("source"), dict) else None
                        )
                    except Exception:
                        name = f"Source {sid}"
                        stype = None
                    val = lobj.get("validate")
                    try:
                        vnorm = (str(val).lower() if val is not None else None)
                    except Exception:
                        vnorm = None
                    enriched.append({
                        "id": sid,
                        "name": name,
                        "type": stype,
                        "local_present": True,
                        "local_validate": vnorm,
                    })
            except Exception:
                pass
            return jsonify({"ok": True, "items": enriched})
        return jsonify({"ok": False, "status": r.status_code, "error": body}), 200
    except Exception as exc:
        return jsonify({"ok": False, "items": [], "message": str(exc)}), 200


@bp.get("/sync-conversations")
def sync_conversations():
    """Ensure local conversations for a given issue are present by pulling from backend if missing.

    Query: issue_id
    """
    issue_id = (request.args.get("issue_id") or "").strip()
    if not issue_id:
        return jsonify({"ok": False, "message": "Missing issue_id"}), 400
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    backend_url: str | None = None
    token_value: str | None = None
    try:
        backend_url = getattr(cfg, "url", None)
        token_value = getattr(cfg, "token", None)
    except Exception:
        backend_url = None
        token_value = None
    # Try env file fallback
    try:
        if not backend_url:
            home = _qalita_home()
            pointer = os.path.join(home, ".current_env")
            if os.path.isfile(pointer):
                with open(pointer, "r", encoding="utf-8") as f:
                    env_path = (f.read() or "").strip()
                if env_path and os.path.isfile(env_path):
                    with open(env_path, "r", encoding="utf-8") as ef:
                        for raw in ef.readlines():
                            line = (raw or "").strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = (k or "").strip().upper()
                            v = (v or "").strip().strip('"').strip("'")
                            if k in ("QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"):
                                backend_url = v
                            if k in ("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN") and not token_value:
                                token_value = v
    except Exception:
        pass
    if not backend_url:
        return jsonify({"ok": False, "message": "Missing backend URL"}), 200
    headers = {"Accept": "application/json"}
    if token_value:
        headers["Authorization"] = f"Bearer {token_value}"
    # List conversations
    try:
        base = str(backend_url).rstrip("/") + f"/api/v1/issues/{issue_id}/studio_conversations"
    except Exception:
        base = str(backend_url) + f"/api/v1/issues/{issue_id}/studio_conversations"
    try:
        r = requests.get(base, headers=headers, timeout=10)
        items = r.json() if r.ok else []
    except Exception:
        items = []
    # Download any missing files
    conv_dir = _studio_conv_dir()
    downloaded = 0
    try:
        for it in (items or []):
            try:
                fname = (it.get("filename") or (it.get("conv_id", "") + ".jsonl")).strip()
            except Exception:
                fname = None
            if not fname:
                continue
            local_path = os.path.join(conv_dir, fname)
            if os.path.isfile(local_path):
                continue
            # fetch download
            try:
                did = it.get("id")
                url = str(backend_url).rstrip("/") + f"/api/v1/issues/{issue_id}/studio_conversations/{did}/download"
            except Exception:
                continue
            try:
                dr = requests.get(url, headers=headers, timeout=20)
                if dr.status_code >= 400:
                    continue
                os.makedirs(conv_dir, exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(dr.content or b"")
                downloaded += 1
            except Exception:
                continue
    except Exception:
        pass
    return jsonify({"ok": True, "downloaded": downloaded})


@bp.post("/upload-conversation")
def upload_conversation():
    """Upload a local conversation file for an issue to the backend.

    Body: { conv_id: str, issue_id: str }
    """
    data = request.get_json(silent=True) or {}
    conv_id = _safe_conv_id((data.get("conv_id") or "").strip())
    issue_id = (data.get("issue_id") or "").strip()
    if not conv_id or not issue_id:
        return jsonify({"ok": False, "message": "Missing conv_id or issue_id"}), 400
    path = _studio_conv_file_for(conv_id)
    if not os.path.isfile(path):
        return jsonify({"ok": False, "message": "Local conversation not found"}), 404
    # Backend context
    cfg = current_app.config.get("QALITA_CONFIG_OBJ")
    backend_url: str | None = None
    token_value: str | None = None
    try:
        backend_url = getattr(cfg, "url", None)
        token_value = getattr(cfg, "token", None)
    except Exception:
        backend_url = None
        token_value = None
    # Try env file fallback
    try:
        if not backend_url:
            home = _qalita_home()
            pointer = os.path.join(home, ".current_env")
            if os.path.isfile(pointer):
                with open(pointer, "r", encoding="utf-8") as f:
                    env_path = (f.read() or "").strip()
                if env_path and os.path.isfile(env_path):
                    with open(env_path, "r", encoding="utf-8") as ef:
                        for raw in ef.readlines():
                            line = (raw or "").strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = (k or "").strip().upper()
                            v = (v or "").strip().strip('"').strip("'")
                            if k in ("QALITA_AGENT_ENDPOINT", "AGENT_ENDPOINT", "QALITA_URL", "URL"):
                                backend_url = v
                            if k in ("QALITA_AGENT_TOKEN", "QALITA_TOKEN", "TOKEN") and not token_value:
                                token_value = v
    except Exception:
        pass
    if not backend_url:
        return jsonify({"ok": False, "message": "Missing backend URL"}), 200
    try:
        with open(path, "rb") as f:
            files = {
                "file": (f"{conv_id}.jsonl", f, "text/plain"),
            }
            data_form = {
                "conv_id": conv_id,
                "filename": f"{conv_id}.jsonl",
            }
            headers = {}
            if token_value:
                headers["Authorization"] = f"Bearer {token_value}"
            url = str(backend_url).rstrip("/") + f"/api/v1/issues/{issue_id}/studio_conversations"
            r = requests.post(url, headers=headers, files=files, data=data_form, timeout=30)
            if r.status_code >= 400:
                try:
                    body = r.json()
                except Exception:
                    body = {"detail": r.text[:200]}
                return jsonify({"ok": False, "status": r.status_code, "error": body}), 200
            return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc)}), 200


@bp.post("/chat")
def studio_chat():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    conv_id = _safe_conv_id((data.get("conv_id") or "").strip())
    issue_id = (data.get("issue_id") or "").strip()
    source_id = (data.get("source_id") or "").strip()
    issue_details = data.get("issue_details") if isinstance(data.get("issue_details"), dict) else None
    # Prefer model from request; else fall back to saved Studio config; else default
    model = (data.get("model") or "").strip()
    if not model:
        try:
            cfg_path = _studio_config_path()
            if os.path.isfile(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    raw = f.read().strip()
                    if raw:
                        cfg = json.loads(raw)
                        model = (cfg.get("model") or "").strip()
        except Exception:
            # Ignore config read errors and continue to use default below
            pass
    if not model:
        model = "gpt-oss:20b"
    if not prompt:
        return jsonify({"ok": False, "message": "Missing prompt"}), 400
    # Streaming toggle via query or body
    stream_flag_raw = (
        (request.args.get("stream") or data.get("stream") or "").strip().lower()
    )
    stream_enabled = stream_flag_raw in ("1", "true", "yes", "on")
    if stream_enabled:

        def generate_stream():
            req = None
            accumulated = ""
            logged = False
            try:
                # Log user message at start of request
                try:
                    _studio_conv_write(conv_id, {"role": "user", "text": prompt, "model": model, "issue_id": issue_id or None, "source_id": source_id or None, "issue_details": issue_details or None})
                except Exception:
                    pass
                # Try attach source details when present
                src_details = None
                try:
                    if source_id:
                        conf = _read_qalita_conf()
                        src_obj = _find_source_by_id(conf, source_id)
                        if isinstance(src_obj, dict):
                            src_details = src_obj
                except Exception:
                    src_details = None

                req = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={"model": model, "prompt": _augment_prompt_with_context(prompt, issue_id, source_id, issue_details, src_details), "stream": True},
                    stream=True,
                    timeout=300,
                )
                if req.status_code != 200:
                    try:
                        body = req.json()
                        msg = (
                            (body.get("error") if isinstance(body, dict) else None)
                            or (body.get("message") if isinstance(body, dict) else None)
                            or str(body)
                        )
                    except Exception:
                        msg = f"Ollama error: {req.status_code}"
                    try:
                        _studio_conv_write(
                            conv_id,
                            {
                                "role": "assistant",
                                "text": accumulated or f"[ERROR] {msg}",
                                "model": model,
                                "ok": False,
                                "status": req.status_code,
                                "error": msg,
                                "stream": True,
                                "issue_id": issue_id or None,
                                "source_id": source_id or None,
                            },
                        )
                        logged = True
                    except Exception:
                        pass
                    yield f"[ERROR] {msg}"
                    return
                for line in req.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if obj.get("response"):
                            piece = obj["response"]
                            accumulated += piece
                            yield piece
                        if obj.get("done"):
                            break
                    except Exception:
                        # Fallback: passthrough raw line
                        accumulated += line
                        yield line
            except GeneratorExit:
                # Client disconnected/aborted
                if req is not None:
                    try:
                        req.close()
                    except Exception:
                        pass
                try:
                    if not logged:
                        _studio_conv_write(
                            conv_id,
                            {
                                "role": "assistant",
                                "text": accumulated,
                                "model": model,
                                "ok": True,
                                "interrupted": True,
                                "stream": True,
                                "issue_id": issue_id or None,
                                "source_id": source_id or None,
                            },
                        )
                        logged = True
                except Exception:
                    pass
                raise
            except Exception as exc:
                try:
                    if not logged:
                        _studio_conv_write(
                            conv_id,
                            {
                                "role": "assistant",
                                "text": accumulated or f"[ERROR] Failed to reach Ollama: {exc}",
                                "model": model,
                                "ok": False,
                                "error": str(exc),
                                "stream": True,
                                "issue_id": issue_id or None,
                                "source_id": source_id or None,
                            },
                        )
                        logged = True
                except Exception:
                    pass
                yield f"[ERROR] Failed to reach Ollama: {exc}"
            finally:
                if req is not None:
                    try:
                        req.close()
                    except Exception:
                        pass
                try:
                    if not logged:
                        _studio_conv_write(
                            conv_id,
                            {
                                "role": "assistant",
                                "text": accumulated,
                                "model": model,
                                "ok": True,
                                "stream": True,
                                "issue_id": issue_id or None,
                                "source_id": source_id or None,
                            },
                        )
                        logged = True
                except Exception:
                    pass

        return Response(stream_with_context(generate_stream()), mimetype="text/plain; charset=utf-8")
    try:
        # Log user message for non-streaming
        try:
            _studio_conv_write(conv_id, {"role": "user", "text": prompt, "model": model, "issue_id": issue_id or None, "source_id": source_id or None, "issue_details": issue_details or None})
        except Exception:
            pass
        # Try attach source details when present
        src_details = None
        try:
            if source_id:
                conf = _read_qalita_conf()
                src_obj = _find_source_by_id(conf, source_id)
                if isinstance(src_obj, dict):
                    src_details = src_obj
        except Exception:
            src_details = None

        r = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": model, "prompt": _augment_prompt_with_context(prompt, issue_id, source_id, issue_details, src_details), "stream": False},
            timeout=60,
        )
        if r.status_code == 200:
            out = r.json().get("response", "")
            try:
                _studio_conv_write(conv_id, {"role": "assistant", "text": out, "model": model, "ok": True, "stream": False, "issue_id": issue_id or None, "source_id": source_id or None})
            except Exception:
                pass
            return jsonify({"ok": True, "response": out, "conv_id": conv_id})
        if r.status_code == 404:
            try:
                _studio_conv_write(conv_id, {"role": "assistant", "text": "", "model": model, "ok": False, "status": r.status_code, "error": "model_not_found", "stream": False})
            except Exception:
                pass
            return (
                jsonify(
                    {
                        "ok": False,
                        "message": f"Model not found in Ollama: '{model}'. Install it with 'ollama pull {model}' or update your Studio model.",
                    }
                ),
                500,
            )
        # Try to surface error body if available
        try:
            err_body = r.json()
        except Exception:
            err_body = {"detail": r.text[:200]}
        try:
            _studio_conv_write(conv_id, {"role": "assistant", "text": "", "model": model, "ok": False, "status": r.status_code, "error": err_body, "stream": False})
        except Exception:
            pass
        return (
            jsonify(
                {
                    "ok": False,
                    "message": f"Ollama error: {r.status_code}",
                    "error": err_body,
                }
            ),
            500,
        )
    except Exception as exc:
        try:
            _studio_conv_write(conv_id, {"role": "assistant", "text": "", "model": model, "ok": False, "error": str(exc), "stream": False})
        except Exception:
            pass
        return jsonify({"ok": False, "message": f"Failed to reach Ollama: {exc}"}), 502
