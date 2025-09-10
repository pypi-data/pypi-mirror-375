import uuid
from collections.abc import Callable
from contextvars import ContextVar, Token
from dataclasses import dataclass

# Pillar
from pillar.callbacks import IsFlaggedCallable, OnFlaggedCallbackType, default_is_flagged, perform_monitoring

# === ID Functions ===
USER_PREFIX = "plr-uid"
SESSION_PREFIX = "plr-sid"


def create_prefixed_id(prefix: str) -> str:
    """Create a prefixed id with a UUID."""
    return f"{prefix}-{uuid.uuid4()!s}"


def create_user_id() -> str:
    """Create a user ID with a prefix."""
    return create_prefixed_id(USER_PREFIX)


def create_session_id() -> str:
    """Create a session ID with a prefix."""
    return create_prefixed_id(SESSION_PREFIX)


# === Context Variables ===

pillar_session_id: ContextVar[str | None] = ContextVar("pillar_session_id", default=None)
pillar_user_id: ContextVar[str | None] = ContextVar("pillar_user_id", default=None)

pillar_is_flagged_fn: ContextVar[IsFlaggedCallable] = ContextVar("pillar_is_flagged_fn", default=default_is_flagged)
pillar_on_flagged_fn: ContextVar[OnFlaggedCallbackType] = ContextVar("pillar_on_flagged_fn", default=perform_monitoring)


@dataclass
class ContextObject:
    pillar_session_id: str | None
    pillar_user_id: str | None
    is_flagged_fn: IsFlaggedCallable | None = None
    on_flagged_fn: OnFlaggedCallbackType | None = None


def get_context_object() -> ContextObject:
    """Get the context object."""
    return ContextObject(
        pillar_session_id=pillar_session_id.get(),
        pillar_user_id=pillar_user_id.get(),
        is_flagged_fn=pillar_is_flagged_fn.get(),
        on_flagged_fn=pillar_on_flagged_fn.get(),
    )


# === Context Variable Helpers ===


def session_id_token(param_session_id: str | None = None) -> Token[str | None]:
    """Create a session ID token - sets the context variable and returns the token."""
    return pillar_session_id.set(param_session_id or pillar_session_id.get() or create_session_id())


def user_id_token(param_user_id: str | None = None) -> Token[str | None]:
    """Create a user ID token - sets the context variable and returns the token."""
    return pillar_user_id.set(param_user_id or pillar_user_id.get() or create_user_id())  # no default


def is_flagged_fn_token(
    param_is_flagged_fn: IsFlaggedCallable | None = None,
) -> Token[IsFlaggedCallable]:
    """Create an is flagged function token - sets the context variable and returns the token."""
    return pillar_is_flagged_fn.set(
        param_is_flagged_fn or pillar_is_flagged_fn.get()  # default is on the context var defention
    )


def on_flagged_fn_token(
    param_on_flagged_fn: OnFlaggedCallbackType | None = None,
) -> Token[OnFlaggedCallbackType]:
    """Create an on flagged function token - sets the context variable and returns the token."""
    return pillar_on_flagged_fn.set(
        param_on_flagged_fn or pillar_on_flagged_fn.get()  # default is on the context var defention
    )


# === Get Context Variables Names ===


def get_fn_name(fn: Callable) -> str:
    """Get the name of a function."""
    if hasattr(fn, "__name__"):
        return str(fn.__name__)
    return str(fn)


def get_on_flagged_fn_name() -> str:
    """Get the name of the on flagged function."""
    fn = pillar_on_flagged_fn.get()
    return get_fn_name(fn)


def get_is_flagged_fn_name() -> str:
    """Get the name of the flagged detector function."""
    fn = pillar_is_flagged_fn.get()
    return get_fn_name(fn)
