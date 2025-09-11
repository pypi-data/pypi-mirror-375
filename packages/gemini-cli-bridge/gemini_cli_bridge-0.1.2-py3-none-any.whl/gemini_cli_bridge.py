#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Dict, List, Optional

import contextlib
import ipaddress
import json
import os
import re
import socket
import subprocess
import urllib.request
from urllib.parse import urlencode, urlparse

from fastmcp import FastMCP


# ---- Constants and MCP initialization ---------------------------------------
_DEFAULT_MAX_OUT = 200_000  # default truncation length
mcp = FastMCP("Gemini")


# --- Config helpers -----------------------------------------------------------
def _get_int_env(name: str, default: int) -> int:
    try:
        val = int(str(os.getenv(name, "")).strip())
        if val > 0:
            return val
    except Exception:
        pass
    return int(default)


def get_max_out() -> int:
    """Return configured output truncation length.

    Env: GEMINI_BRIDGE_MAX_OUT (int, >0). Default: _DEFAULT_MAX_OUT.
    """
    return _get_int_env("GEMINI_BRIDGE_MAX_OUT", _DEFAULT_MAX_OUT)


def _truncate(s: Optional[str]) -> str:
    """Truncate string to configured length with marker when needed."""
    if s is None:
        return ""
    limit = get_max_out()
    if len(s) <= limit:
        return s
    return s[:limit] + "\n...[truncated]..."


def _allowed_path_prefixes() -> tuple:
    """Whitelist for extending PATH via env, safe-by-default.

    - Defaults to common system prefixes.
    - Can extend via GEMINI_BRIDGE_ALLOWED_PATH_PREFIXES (colon-separated).
    """
    defaults = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/sbin",
    ]
    extra = []
    raw = os.getenv("GEMINI_BRIDGE_ALLOWED_PATH_PREFIXES", "").strip()
    if raw:
        for p in raw.split(":"):
            p = p.strip()
            if p and os.path.isabs(p):
                extra.append(p)
    # de-dup while preserving order
    seen = set()
    items = []
    for p in [*defaults, *extra]:
        if p not in seen:
            seen.add(p)
            items.append(p)
    return tuple(items)


def _unify_timeout(provided: Optional[int], default: int) -> int:
    """Return final timeout: provided > env > default."""
    if isinstance(provided, int) and provided > 0:
        return provided
    return _get_int_env("GEMINI_BRIDGE_DEFAULT_TIMEOUT_S", default)

@mcp.tool()  # important: decorator requires parentheses
def gemini_prompt(
    prompt: str,
    model: str = "gemini-2.5-pro",
    include_dirs: Optional[List[str]] = None,
    timeout_s: Optional[int] = None,
    extra_args: Optional[List[str]] = None,
) -> str:
    """Run local `gemini` CLI non-interactively; return structured JSON."""
    cmd = ["gemini", "-m", model, "-p", prompt]
    if include_dirs:
        cmd += ["--include-directories", ",".join(include_dirs)]
    if extra_args:
        for a in extra_args:
            if isinstance(a, str) and a.startswith("-"):
                cmd.append(a)
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


# --- Helpers -----------------------------------------------------------------
def _env_with_path(extra_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    env = os.environ.copy()
    # Disable colors for easier client parsing
    env["NO_COLOR"] = "1"
    base_path = env.get("PATH", "")
    # default safe additions
    base_path = base_path + ":/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

    # Optional: allow extending PATH via a safe whitelist
    extras_raw = os.getenv("GEMINI_BRIDGE_EXTRA_PATHS", "").strip()
    if extras_raw:
        allowed = _allowed_path_prefixes()
        extras: List[str] = []
        for p in extras_raw.split(":"):
            p = p.strip()
            if not p:
                continue
            try:
                rp = os.path.realpath(p)
                if os.path.isabs(rp) and any(rp.startswith(pref) for pref in allowed) and os.path.isdir(rp):
                    extras.append(rp)
            except Exception:
                continue
        if extras:
            base_path = base_path + ":" + ":".join(extras)
    env["PATH"] = base_path
    if extra_env:
        for k, v in extra_env.items():
            if not (isinstance(k, str) and isinstance(v, str)):
                continue
            if k.upper() == "PATH":
                # Safety: do not allow overriding PATH
                continue
            env[k] = v
    return env


def _run(
    cmd: List[str],
    timeout_s: Optional[int] = None,
    *,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None,
    raise_on_error: bool = True,
) -> Dict[str, object]:
    """Run subprocess and return structured result.
    Returns: {cmd: [...], exit_code: int, stdout: str, stderr: str}.
    When raise_on_error is True, raises RuntimeError on non-zero exit.
    """
    to = _unify_timeout(timeout_s, default=120)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=to,
        env=_env_with_path(env),
        cwd=cwd,
    )
    out = _truncate(proc.stdout)
    err = _truncate(proc.stderr)
    if raise_on_error and proc.returncode != 0:
        raise RuntimeError(err.strip() or f"command exit {proc.returncode}: {' '.join(cmd)}")
    return {
        "cmd": cmd,
        "exit_code": proc.returncode,
        "stdout": out,
        "stderr": err,
    }


def _run_gemini_and_format_output(cmd: List[str], timeout_s: Optional[int] = None) -> str:
    """Runs a gemini command and returns the standardized JSON response."""
    res = _run(cmd, timeout_s=timeout_s, raise_on_error=False)
    ok = res.get("exit_code", 1) == 0
    return json.dumps(
        {
            "ok": ok,
            "exit_code": res.get("exit_code"),
            "stdout": str(res.get("stdout", "")).strip(),
            "stderr": str(res.get("stderr", "")).strip(),
        },
        ensure_ascii=False,
    )


def _at_ref(path: str) -> str:
    """Quote a path as an @"..." reference safely (handles spaces/quotes)."""
    raw = path[1:] if isinstance(path, str) and path.startswith("@") else str(path)
    safe = raw.replace('"', '\\"')
    return f'@"{safe}"'


def _is_private_url(url: str) -> bool:
    """Heuristically block private/loopback/link-local URLs (SSRF guard)."""
    try:
        u = urlparse(url)
        if u.scheme not in {"http", "https"}:
            return True
        host = u.hostname or ""
        # Explicit loopback/local hostname
        if host in {"localhost"}:
            return True
        # Resolve all addresses
        for fam, _, _, _, sockaddr in socket.getaddrinfo(host, None):
            ip = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                return True
        return False
    except Exception:
        # Treat unresolvable URLs as unsafe
        return True


@mcp.tool()
def gemini_version(timeout_s: Optional[int] = None) -> str:
    """Return installed gemini CLI version (gemini --version) as JSON."""
    return _run_gemini_and_format_output(["gemini", "--version"], timeout_s=timeout_s)


@mcp.tool()
def gemini_mcp_list(scope: Optional[str] = None, timeout_s: Optional[int] = None) -> str:
    """List MCP servers configured in gemini CLI (gemini mcp list). Scope: user|project."""
    cmd = ["gemini", "mcp", "list"]
    if scope in {"user", "project"}:
        cmd += ["--scope", scope]
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


@mcp.tool()
def gemini_mcp_add(
    name: str,
    command_or_url: str,
    transport: str = "stdio",  # stdio|http|sse
    args: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    scope: str = "project",  # user|project
    timeout_ms: Optional[int] = None,
    trust: bool = False,
    description: Optional[str] = None,
    include_tools: Optional[List[str]] = None,
    exclude_tools: Optional[List[str]] = None,
    timeout_s: Optional[int] = None,
) -> str:
    """Add an MCP server via gemini CLI (gemini mcp add ...).
    transport: stdio|http|sse; for stdio pass executable, for http/sse pass URL.
    headers are only valid for http/sse. Returns CLI stdout.
    """
    cmd = ["gemini", "mcp", "add", name]

    # transport
    if transport in {"http", "sse"}:
        cmd += ["--transport", transport, command_or_url]
    else:
    # default: stdio
        cmd += [command_or_url]
        if args:
            cmd += args

    # scope
    if scope in {"user", "project"}:
        cmd += ["--scope", scope]

    # env vars (-e KEY=VAL)
    if env_vars:
        for k, v in env_vars.items():
            if k and v is not None:
                cmd += ["-e", f"{k}={v}"]

    # headers (-H "K: V")
    if headers and transport in {"http", "sse"}:
        for hk, hv in headers.items():
            cmd += ["-H", f"{hk}: {hv}"]

    if timeout_ms is not None and isinstance(timeout_ms, int) and timeout_ms > 0:
        cmd += ["--timeout", str(timeout_ms)]
    if trust:
        cmd += ["--trust"]
    if description:
        cmd += ["--description", description]
    if include_tools:
        cmd += ["--include-tools", ",".join(include_tools)]
    if exclude_tools:
        cmd += ["--exclude-tools", ",".join(exclude_tools)]
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


@mcp.tool()
def gemini_mcp_remove(name: str, scope: str = "project", timeout_s: Optional[int] = None) -> str:
    """Remove an MCP server from gemini CLI (gemini mcp remove <name>)."""
    cmd = ["gemini", "mcp", "remove", name]
    if scope in {"user", "project"}:
        cmd += ["--scope", scope]
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


@mcp.tool()
def gemini_web_fetch(
    prompt: str,
    urls: List[str],
    model: str = "gemini-2.5-pro",
    include_dirs: Optional[List[str]] = None,
    approval_mode: Optional[str] = None,  # default|auto_edit|yolo
    yolo: bool = False,
    checkpointing: bool = False,
    extra_args: Optional[List[str]] = None,
    timeout_s: Optional[int] = None,
) -> str:
    """Convenience wrapper: inject URLs into prompt to trigger CLI WebFetch.
    Note: WebFetch is a CLI built-in; the model decides whether to call it.
    """
    urls = [u for u in (urls or []) if isinstance(u, str) and (u.startswith("http://") or u.startswith("https://"))]
    if not urls:
        raise ValueError("urls must contain at least one http(s) link")

    composed = f"{prompt.strip()}\n\n" + "\n".join(urls)
    cmd = ["gemini", "-m", model, "-p", composed]
    if include_dirs:
        cmd += ["--include-directories", ",".join(include_dirs)]
    if checkpointing:
        cmd += ["--checkpointing"]
    if approval_mode in {"default", "auto_edit", "yolo"}:
        cmd += ["--approval-mode", approval_mode]
    elif yolo:
        cmd += ["--yolo"]
    if extra_args:
        for a in extra_args:
            if isinstance(a, str) and a.startswith("-"):
                cmd.append(a)
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


@mcp.tool()
def gemini_extensions_list(timeout_s: Optional[int] = None) -> str:
    """List available Gemini CLI extensions (gemini --list-extensions)."""
    return _run_gemini_and_format_output(["gemini", "--list-extensions"], timeout_s=timeout_s)


@mcp.tool()
def gemini_prompt_plus(
    prompt: str,
    model: str = "gemini-2.5-pro",
    include_dirs: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    approval_mode: Optional[str] = None,  # default|auto_edit|yolo
    yolo: bool = False,
    checkpointing: bool = False,
    extra_args: Optional[List[str]] = None,
    timeout_s: Optional[int] = None,
) -> str:
    """Advanced non-interactive run with attachments/approval/checkpoint/dirs/flags.
    - attachments: file/dir paths appended as @path at the end of prompt.
    - approval_mode: default|auto_edit|yolo; if unset and yolo=True, add --yolo.
    """
    final_prompt = prompt or ""
    if attachments:
        at_refs = " ".join(_at_ref(p) for p in attachments)
        if at_refs:
            final_prompt = (final_prompt.rstrip() + "\n\n" + at_refs).strip()

    cmd = ["gemini", "-m", model]
    if include_dirs:
        cmd += ["--include-directories", ",".join(include_dirs)]
    if checkpointing:
        cmd += ["--checkpointing"]
    if approval_mode in {"default", "auto_edit", "yolo"}:
        cmd += ["--approval-mode", approval_mode]
    elif yolo:
        cmd += ["--yolo"]

    cmd += ["-p", final_prompt]
    if extra_args:
        for a in extra_args:
            if isinstance(a, str) and a.startswith("-"):
                cmd.append(a)
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


@mcp.tool()
def gemini_search(
    query: str,
    model: str = "gemini-2.5-pro",
    include_dirs: Optional[List[str]] = None,
    approval_mode: Optional[str] = None,
    yolo: bool = True,
    checkpointing: bool = False,
    extra_args: Optional[List[str]] = None,
    timeout_s: Optional[int] = None,
) -> str:
    """Lightweight search: guide the model to use built-in GoogleSearch and cite sources.
    Note: tool invocation is model-driven; default yolo=True to avoid interactive prompts.
    """
    guidance = (
        "Please use the built-in GoogleSearch tool to find up-to-date, authoritative sources, "
        "then synthesize an answer with citations. Prioritize primary sources and include URLs.\n\n"
    )
    final_prompt = guidance + f"Search task: {query.strip()}"

    cmd = ["gemini", "-m", model]
    if include_dirs:
        cmd += ["--include-directories", ",".join(include_dirs)]
    if checkpointing:
        cmd += ["--checkpointing"]
    if approval_mode in {"default", "auto_edit", "yolo"}:
        cmd += ["--approval-mode", approval_mode]
    elif yolo:
        cmd += ["--yolo"]
    cmd += ["-p", final_prompt]
    if extra_args:
        for a in extra_args:
            if isinstance(a, str) and a.startswith("-"):
                cmd.append(a)
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


@mcp.tool()
def gemini_prompt_with_memory(
    prompt: str,
    memory_paths: Optional[List[str]] = None,
    attachments: Optional[List[str]] = None,
    model: str = "gemini-2.5-pro",
    include_dirs: Optional[List[str]] = None,
    approval_mode: Optional[str] = None,
    yolo: bool = False,
    checkpointing: bool = False,
    extra_args: Optional[List[str]] = None,
    timeout_s: int = 180,
) -> str:
    """Inject memory_paths as high-priority context, then run non-interactively.
    - memory_paths: authoritative project/system memory (e.g., GEMINI.md, conventions).
    - attachments: additional files/dirs injected as @path.
    """
    blocks: List[str] = []
    if memory_paths:
        at_mem = "\n".join(_at_ref(p) for p in memory_paths)
        if at_mem:
            blocks.append(
                "[HIGH-PRIORITY CONTEXT]\n"
                "Use the following project memory and conventions as authoritative context.\n\n"
                + at_mem
            )
    if prompt:
        blocks.append(prompt.strip())
    if attachments:
        at_refs = "\n".join(_at_ref(p) for p in attachments)
        if at_refs:
            blocks.append(at_refs)
    final_prompt = "\n\n".join(blocks).strip()

    cmd = ["gemini", "-m", model]
    if include_dirs:
        cmd += ["--include-directories", ",".join(include_dirs)]
    if checkpointing:
        cmd += ["--checkpointing"]
    if approval_mode in {"default", "auto_edit", "yolo"}:
        cmd += ["--approval-mode", approval_mode]
    elif yolo:
        cmd += ["--yolo"]
    cmd += ["-p", final_prompt]
    if extra_args:
        for a in extra_args:
            if isinstance(a, str) and a.startswith("-"):
                cmd.append(a)
    return _run_gemini_and_format_output(cmd, timeout_s=timeout_s)


# --- General system/network tools --------------------------------------------

@mcp.tool()
def Shell(cmd: str, cwd: Optional[str] = None, timeout_s: Optional[int] = None) -> str:
    """Execute a shell command; return JSON {code, stdout, stderr}. Disabled by default; set MCP_BASH_ALLOW=1 to enable."""
    if os.getenv("MCP_BASH_ALLOW", "0") != "1":
        return json.dumps({"code": 126, "stdout": "", "stderr": "Shell disabled (set MCP_BASH_ALLOW=1)"}, ensure_ascii=False)
    try:
        to = _unify_timeout(timeout_s, default=120)
        completed = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            env=_env_with_path({}),
            capture_output=True,
            text=True,
            timeout=to,
        )
        stdout = _truncate(completed.stdout)
        stderr = _truncate(completed.stderr)
        return json.dumps({"code": completed.returncode, "stdout": stdout, "stderr": stderr}, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        return json.dumps({"code": 124, "stdout": "", "stderr": f"timeout after {timeout_s}s"}, ensure_ascii=False)


@mcp.tool()
def FindFiles(pattern: str = "*", base: str = ".", recursive: bool = True) -> str:
    """Find files; return JSON array of paths. Supports recursion."""
    base_path = Path(base).expanduser().resolve()
    try:
        if recursive and "**" not in pattern:
            pattern = f"**/{pattern}"
        matches = [str(p) for p in base_path.glob(pattern) if p.exists()]
        return json.dumps(matches, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def ReadFile(path: str) -> str:
    """Read a text file (utf-8, ignore errors). Raises if missing."""
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(str(p))
    return p.read_text(encoding="utf-8", errors="ignore")


@mcp.tool()
def ReadFolder(path: str = ".", recursive: bool = False, max_entries: int = 2000) -> str:
    """Read a directory; return JSON array of entries (optionally recursive)."""
    root = Path(path).expanduser().resolve()
    items: List[str] = []
    try:
        if recursive:
            for dirpath, dirnames, filenames in os.walk(root):
                for d in dirnames:
                    items.append(str(Path(dirpath, d)) + "/")
                for f in filenames:
                    items.append(str(Path(dirpath, f)))
                if len(items) >= max_entries:
                    break
        else:
            for child in sorted(root.iterdir()):
                items.append(str(child) + ("/" if child.is_dir() else ""))
        return json.dumps(items[:max_entries], ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def ReadManyFiles(paths: List[str], ignore_missing: bool = True) -> str:
    """Read multiple files; return JSON object {path: content}."""
    result: Dict[str, str] = {}
    for p0 in paths or []:
        p = Path(str(p0)).expanduser().resolve()
        if not p.exists() or not p.is_file():
            if ignore_missing:
                continue
            raise FileNotFoundError(str(p))
        try:
            result[str(p)] = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            result[str(p)] = f"<error: {e}>"
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def SaveMemory(path: str, content: str, mode: str = "append") -> str:
    """Save content to path; mode=append|overwrite; return JSON {ok, bytes}."""
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    data = content or ""
    try:
        if mode == "overwrite":
            p.write_text(data, encoding="utf-8")
        else:
            with p.open("a", encoding="utf-8") as f:
                f.write(data)
        return json.dumps({"ok": True, "bytes": len(data)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)


@mcp.tool()
def SearchText(pattern: str, path: str, case_insensitive: bool = False) -> str:
    """Search text within a file; return JSON array [{line, text}]."""
    p = Path(path).expanduser().resolve()
    results: List[Dict[str, object]] = []
    if not p.exists() or not p.is_file():
        return json.dumps(results, ensure_ascii=False)
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        flags = re.MULTILINE | (re.IGNORECASE if case_insensitive else 0)
        for i, line in enumerate(text.splitlines(), start=1):
            if re.search(pattern, line, flags=flags):
                results.append({"line": i, "text": line})
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
def WriteFile(path: str, content: str) -> str:
    """Write a UTF-8 text file, creating parents as needed. Return "ok"."""
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return "ok"


@mcp.tool()
def Edit(path: str, find: str, replace: str, count: int = 0) -> str:
    """String replace; count=0 means replace all. Return JSON {"replaced": n}."""
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(str(p))
    s = p.read_text(encoding="utf-8", errors="ignore")
    if count == 0:
        replaced = s.count(find)
        s2 = s.replace(find, replace)
    else:
        replaced = min(s.count(find), max(count, 0))
        s2 = s.replace(find, replace, replaced)
    p.write_text(s2, encoding="utf-8")
    return json.dumps({"replaced": replaced}, ensure_ascii=False)


# Tools included: Edit, FindFiles, GoogleSearch, ReadFile, ReadFolder, ReadManyFiles, SaveMemory, SearchText, Shell, WebFetch, WriteFile.


@mcp.tool()
def WebFetch(url: str, timeout_s: int = 15) -> str:
    """Minimal web fetch using the requests library; return JSON {ok,status,content?,error?}."""
    data: Dict[str, object] = {"url": url, "ok": False, "status": None, "content": None, "error": None}
    # Basic SSRF guard
    if _is_private_url(url):
        data["error"] = "Blocked private/loopback URL"
        return json.dumps(data, ensure_ascii=False)
    headers = {"User-Agent": "gemini-cli-bridge/1.0"}
    try:
        import requests  # keep import local
        r = requests.get(url, headers=headers, timeout=timeout_s)
        content = r.text
        limit = get_max_out()  # use configured max output
        if len(content) > limit:
            content = content[:limit] + "\n...[truncated]..."
        data.update({"ok": bool(r.ok), "status": r.status_code, "content": content})
    except Exception as e:
        data["error"] = str(e)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
def GoogleSearch(
    query: str,
    limit: int = 5,
    cse_id: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-pro",
    timeout_s: int = 120,
    mode: Optional[str] = None,  # auto | gemini_cli | gcs
) -> str:
    """Search tool (defaults to Gemini CLI built-in GoogleSearch).

        Modes:
        - mode="gemini_cli": force CLI built-in (no keys; requires signed-in gemini CLI)
        - mode="gcs": force Google Programmable Search (requires GOOGLE_CSE_ID + GOOGLE_API_KEY)
        - mode=None/"auto": auto-select (use gcs if both keys present, else gemini_cli)

        Returns JSON:
        - gemini_cli: { ok: true, mode: "gemini_cli", answer: string }
        - gcs: { ok: true, mode: "gcs", results: [{title, link, snippet}] }
            on error: { ok: false, error, results? }
        """
    selected = (mode or "auto").strip().lower()
    cse = cse_id or os.getenv("GOOGLE_CSE_ID")
    key = api_key or os.getenv("GOOGLE_API_KEY")

    # select mode
    use_cli = False
    if selected == "gemini_cli":
        use_cli = True
    elif selected == "gcs":
        use_cli = False
    else:  # auto
        use_cli = not (cse and key)

    # built-in path: call gemini_search (non-interactive, yolo=True)
    if use_cli:
        try:
            # reuse gemini_search tool logic
            answer = gemini_search(query=query, model=model, yolo=True, timeout_s=timeout_s)
            return json.dumps({"ok": True, "mode": "gemini_cli", "answer": answer}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"ok": False, "mode": "gemini_cli", "error": str(e)}, ensure_ascii=False)

    # GCS mode (requires key + cse)
    if not (cse and key):
        return json.dumps({
            "ok": False,
            "mode": "gcs",
            "results": [],
            "error": "GOOGLE_CSE_ID/GOOGLE_API_KEY not provided",
        }, ensure_ascii=False)
    try:
        params = {
            "key": key,
            "cx": cse,
            "q": query,
            "num": max(1, min(int(limit or 5), 10)),  # API allows up to 10 per call
        }
        url = f"https://www.googleapis.com/customsearch/v1?{urlencode(params)}"
        headers = {"User-Agent": "gemini-cli-bridge/1.0"}
        req = urllib.request.Request(url, headers=headers)
        with contextlib.closing(urllib.request.urlopen(req, timeout=timeout_s)) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            raw = resp.read().decode(charset, errors="ignore")
        data = json.loads(raw or "{}")
        items = data.get("items", []) or []
        results = []
        for it in items:
            results.append({
                "title": it.get("title"),
                "link": it.get("link"),
                "snippet": it.get("snippet"),
            })
        return json.dumps({"ok": True, "mode": "gcs", "results": results}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"ok": False, "mode": "gcs", "results": [], "error": str(e)}, ensure_ascii=False)

@mcp.tool()
def GeminiGoogleSearch(
    query: str,
    limit: int = 5,
    cse_id: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-pro",
    timeout_s: Optional[int] = None,
    mode: Optional[str] = None,
) -> str:
    """Alias to GoogleSearch to avoid tool name collisions in some IDEs."""
    return GoogleSearch(query=query, limit=limit, cse_id=cse_id, api_key=api_key, model=model, timeout_s=timeout_s, mode=mode)

if __name__ == "__main__":
    mcp.run()  # default STDIO transport

# 供 console_script 使用
def main() -> None:
    """Entry point for uvx/pipx console_script."""
    mcp.run()
