"""Defensive tool-execution isolation and resource controls.

This is a defense-in-depth boundary, not a replacement for a kernel/container
sandbox. Dangerous permissions are denied before execution; approved handlers
run in a short-lived child process with CPU/address-space/file-size limits and
are killed on timeout.
"""
from __future__ import annotations

import multiprocessing as mp
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable

from .policy import PermissionPolicy


@dataclass(frozen=True)
class SandboxLimits:
    timeout_seconds: float = 2.0
    max_output_chars: int = 16_384
    cpu_seconds: int = 2
    memory_bytes: int = 256 * 1024 * 1024
    max_file_bytes: int = 1 * 1024 * 1024

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0 or self.max_output_chars <= 0:
            raise ValueError("timeout and output limits must be positive")
        if self.cpu_seconds < 1 or self.memory_bytes < 1 or self.max_file_bytes < 1:
            raise ValueError("resource limits must be positive")


@dataclass(frozen=True)
class SandboxResult:
    status: str
    value: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    output_truncated: bool = False

    @property
    def ok(self) -> bool:
        return self.status == "PASS"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "value": self.value,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 3),
            "output_truncated": self.output_truncated,
        }


def _apply_limits(limits: SandboxLimits) -> None:
    """Best-effort Unix resource limits; Windows still gets process/timeout isolation."""
    if os.name != "posix":
        return
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (limits.cpu_seconds, limits.cpu_seconds))
        resource.setrlimit(resource.RLIMIT_AS, (limits.memory_bytes, limits.memory_bytes))
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits.max_file_bytes, limits.max_file_bytes))
        # Prevent the child from creating an unbounded process tree.
        if hasattr(resource, "RLIMIT_NPROC"):
            resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
    except (ImportError, OSError, ValueError):
        pass


def _child_entry(conn, handler: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any], limits: SandboxLimits) -> None:
    try:
        _apply_limits(limits)
        with tempfile.TemporaryDirectory(prefix="agent-passport-sandbox-") as workdir:
            os.chdir(workdir)
            try:
                value = handler(*args, **kwargs)
                # Avoid transporting an unexpectedly huge textual result.
                text = repr(value)
                if len(text) > limits.max_output_chars:
                    conn.send(("PASS", text[:limits.max_output_chars], True, None))
                else:
                    conn.send(("PASS", value, False, None))
            except BaseException as exc:  # return a controlled error to parent
                conn.send(("ERROR", None, False, f"{type(exc).__name__}: {exc}"))
    except BaseException as exc:
        try:
            conn.send(("ERROR", None, False, f"SandboxError: {type(exc).__name__}: {exc}"))
        except Exception:
            pass
    finally:
        conn.close()


def _execute_threaded(handler: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any], limits: SandboxLimits) -> SandboxResult:
    """Fallback path for non-pickleable callables on Windows and other spawn-only systems."""
    payload: dict[str, Any] = {"value": None, "truncated": False, "error": None}

    def worker() -> None:
        try:
            value = handler(*args, **kwargs)
            text = repr(value)
            payload["value"] = value if len(text) <= limits.max_output_chars else text[: limits.max_output_chars]
            payload["truncated"] = len(text) > limits.max_output_chars
        except BaseException as exc:  # pragma: no cover - exercised by tests via status checks
            payload["error"] = f"{type(exc).__name__}: {exc}"

    started = time.monotonic()
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(limits.timeout_seconds)
    duration_ms = (time.monotonic() - started) * 1000

    if thread.is_alive():
        return SandboxResult("TIMEOUT", error="tool exceeded sandbox timeout", duration_ms=duration_ms)
    if payload["error"] is not None:
        return SandboxResult("ERROR", error=payload["error"], duration_ms=duration_ms)
    return SandboxResult("PASS", payload["value"], duration_ms=duration_ms, output_truncated=payload["truncated"])


class ToolSandbox:
    """Execute an already-authorized tool handler in a bounded child process."""

    def __init__(self, policy: PermissionPolicy, *, limits: SandboxLimits | None = None):
        self.policy = policy
        self.limits = limits or SandboxLimits()

    def execute(self, handler: Callable[..., Any], requested_permissions: set[str], *args, **kwargs) -> SandboxResult:
        if self.policy.evaluate(requested_permissions).value != "ALLOW":
            return SandboxResult("DENY", error="tool permissions rejected by sandbox policy")
        if not callable(handler):
            return SandboxResult("DENY", error="tool handler is not callable")

        try:
            methods = mp.get_all_start_methods()
            method = "fork" if "fork" in methods else methods[0]
            ctx = mp.get_context(method)
            parent, child = ctx.Pipe(duplex=False)
            proc = ctx.Process(target=_child_entry, args=(child, handler, args, kwargs, self.limits), daemon=True)
            started = time.monotonic()
            proc.start()
            child.close()
            proc.join(self.limits.timeout_seconds)
            duration_ms = (time.monotonic() - started) * 1000
            if proc.is_alive():
                proc.kill()
                proc.join()
                parent.close()
                return SandboxResult("TIMEOUT", error="tool exceeded sandbox timeout", duration_ms=duration_ms)
            if parent.poll(0.1):
                status, value, truncated, error = parent.recv()
                parent.close()
                return SandboxResult(status, value, error, duration_ms, truncated)
            parent.close()
            return SandboxResult("ERROR", error=f"sandbox worker exited with code {proc.exitcode}", duration_ms=duration_ms)
        except (AttributeError, TypeError, OSError, RuntimeError, ValueError):
            return _execute_threaded(handler, args, kwargs, self.limits)
