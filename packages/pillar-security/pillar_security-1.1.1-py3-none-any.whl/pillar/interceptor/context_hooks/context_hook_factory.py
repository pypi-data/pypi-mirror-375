from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pillar.interceptor.context_hooks.context_framework_adapter import ContextFrameworkAdapter

if TYPE_CHECKING:
    from pillar.client import Pillar


def _sync_context_hook_implementation(
    pillar: "Pillar",
    adapter: ContextFrameworkAdapter,
    wrapped: Callable,
    instance: Any,
    args: tuple,
    kwargs: dict,
) -> Any:
    """Core logic for the synchronous context hook - with side effects.
    It will call the original function and then extract the context, inject it into the context,
    and then return the original function result.
    """
    # 1. Call Original Function
    run_obj = wrapped(*args, **kwargs)
    try:
        # 2. Extract Context using Adapter
        context_data = adapter.extract_context(run_obj, args, kwargs)

        # 3. Process Context
        adapter.process_context(pillar, context_data)

        # 4. Return the original function result
        return run_obj
    except Exception as e:
        pillar.logger.error(f"Exception in context hook: {e}", exc_info=True)
        return run_obj


async def _async_context_hook_implementation(
    pillar: "Pillar",
    adapter: ContextFrameworkAdapter,
    wrapped: Callable,
    instance: Any,
    args: tuple,
    kwargs: dict,
) -> Any:
    """Core logic for the asynchronous context hook - with side effects.
    It will call the original function and then extract the context, inject it into the context,
    and then return the original function result.
    """
    # 1. Call Original Function
    run_obj = await wrapped(*args, **kwargs)
    try:
        # 2. Extract Context using Adapter
        context_data = adapter.extract_context(run_obj, args, kwargs)

        # 3. Process Context
        await adapter.process_context_async(pillar, context_data)

        # 4. Return the original function result
        return run_obj
    except Exception as e:
        pillar.logger.error(f"Exception in context hook: {e}", exc_info=True)
        return run_obj


def create_context_hook(pillar: "Pillar", adapter: ContextFrameworkAdapter) -> Callable:
    """
    Creates a context hook function (sync or async) based on the provided adapter.
    The adapter instance dictates whether the returned hook is sync or async via adapter.is_async.
    """
    is_async_hook = adapter.is_async

    if is_async_hook:
        # Define the wrapper hook that will be decorated
        async def async_hook_wrapper(wrapped: Callable, instance: Any, args: tuple, kwargs: dict) -> Any:
            """Async hook wrapper that calls the core implementation."""
            return await _async_context_hook_implementation(pillar, adapter, wrapped, instance, args, kwargs)

        return async_hook_wrapper
    else:
        # Define the wrapper hook that will be decorated
        def sync_hook_wrapper(wrapped: Callable, instance: Any, args: tuple, kwargs: dict) -> Any:
            """Sync hook wrapper that calls the core implementation."""
            return _sync_context_hook_implementation(pillar, adapter, wrapped, instance, args, kwargs)

        return sync_hook_wrapper
