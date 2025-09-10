from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pillar.errors import PillarBlockError
from pillar.interceptor.hooks.framework_adapter import ExtractedInput, FrameworkAdapter

if TYPE_CHECKING:
    from pillar.client import Pillar


# --- Private Hook Implementations ---


def _sync_hook_implementation(
    pillar: "Pillar",
    adapter: FrameworkAdapter,
    wrapped: Callable,
    instance: Any,
    args: tuple,
    kwargs: dict,
) -> Any:
    """Core logic for the synchronous hook."""
    log_function_name = f"{adapter.provider_name} sync call"
    extracted: ExtractedInput | None = None
    try:
        # 1. Extract Input using Adapter
        try:
            extracted = adapter.extract_input(args, kwargs)
            log_function_name = f"{adapter.provider_name} sync {extracted.api_type.value}"
        except ValueError as e:
            pillar.logger.error(f"Missing essential arguments for {log_function_name}: {e}")
            return wrapped(*args, **kwargs)

        # 2. Format Input for Pillar
        messages_to_analyze, original_formatting_metadata = adapter.format_input_for_pillar(pillar, extracted)

        # 3. Analyze Input (Sync)
        processed_input = pillar.analyze_sync(
            messages=messages_to_analyze,
            model=extracted.model,
            provider=adapter.provider_name,
            tools=extracted.tools,
        )

        # 4. Format Input back for LLM
        final_input_data = adapter.format_output_from_pillar(
            pillar, processed_input, original_formatting_metadata, extracted
        )

        kwargs_to_llm = {
            **extracted.original_kwargs,
            extracted.input_arg_name: final_input_data,
        }

        # 5. Call Original Function
        result = wrapped(*args, **kwargs_to_llm)

        # 6. Handle Output (Stream or Non-Stream)
        if extracted.stream:
            return adapter.handle_sync_stream(
                pillar=pillar,
                extracted_input=extracted,
                original_stream=result,
            )
        else:
            # 7. Extract Output for Pillar
            output_messages = adapter.extract_output_for_pillar(pillar, result, extracted)

            # 8. Analyze Output (Sync)
            if output_messages:
                _ = pillar.analyze_sync(
                    messages=output_messages,
                    model=extracted.model,
                    provider=adapter.provider_name,
                    tools=extracted.tools,
                )
            else:
                pillar.logger.warning(f"No output messages to analyze for {log_function_name}")

            return result

    except PillarBlockError as blocking_error:
        raise blocking_error
    except Exception as e:
        fallback_kwargs = extracted.original_kwargs if extracted else kwargs
        pillar.logger.error(f"Exception in generic {log_function_name} hook: {e}", exc_info=True)
        try:
            pillar.logger.warning(f"Falling back to original call for {log_function_name} due to hook error.")
            return wrapped(*args, **fallback_kwargs)
        except Exception as original_call_error:
            pillar.logger.error(
                f"Original {log_function_name} failed after hook error: {original_call_error}",
                exc_info=True,
            )
            raise original_call_error


async def _async_hook_implementation(
    pillar: "Pillar",
    adapter: FrameworkAdapter,
    wrapped: Callable,
    instance: Any,
    args: tuple,
    kwargs: dict,
) -> Any:
    """Core logic for the asynchronous hook."""
    log_function_name = f"{adapter.provider_name} async call"
    extracted: ExtractedInput | None = None
    try:
        # 1. Extract Input using Adapter
        try:
            extracted = adapter.extract_input(args, kwargs)
            log_function_name = f"{adapter.provider_name} async {extracted.api_type.value}"
        except ValueError as e:
            pillar.logger.error(f"Missing essential arguments for {log_function_name}: {e}")
            return await wrapped(*args, **kwargs)

        # 2. Format Input for Pillar
        messages_to_analyze, original_formatting_metadata = adapter.format_input_for_pillar(pillar, extracted)

        # 3. Analyze Input (Async)
        processed_input = await pillar.analyze_async(
            messages=messages_to_analyze,
            model=extracted.model,
            provider=adapter.provider_name,
            tools=extracted.tools,
        )

        # 4. Format Input back for LLM
        final_input_data = adapter.format_output_from_pillar(
            pillar, processed_input, original_formatting_metadata, extracted
        )

        kwargs_to_llm = {
            **extracted.original_kwargs,
            extracted.input_arg_name: final_input_data,
        }

        # 5. Call Original Function
        result = await wrapped(*args, **kwargs_to_llm)
        # 6. Handle Output (Stream or Non-Stream)
        if extracted.stream:
            return adapter.handle_async_stream(
                pillar=pillar,
                extracted_input=extracted,
                original_stream=result,
            )
        else:
            # 7. Extract Output for Pillar
            output_messages = adapter.extract_output_for_pillar(pillar, result, extracted)
            # 8. Analyze Output (Async)
            if output_messages:
                _ = await pillar.analyze_async(
                    messages=output_messages,
                    model=extracted.model,
                    provider=adapter.provider_name,
                    tools=extracted.tools,
                )
            else:
                pillar.logger.warning(f"No output messages to analyze for {log_function_name}")

            return result

    except PillarBlockError as blocking_error:
        raise blocking_error
    except Exception as e:
        fallback_kwargs = extracted.original_kwargs if extracted else kwargs
        pillar.logger.error(f"Exception in generic {log_function_name} hook: {e}", exc_info=True)
        try:
            pillar.logger.warning(f"Falling back to original call for {log_function_name} due to hook error.")
            return await wrapped(*args, **fallback_kwargs)
        except Exception as original_call_error:
            pillar.logger.error(
                f"Original {log_function_name} failed after hook error: {original_call_error}",
                exc_info=True,
            )
            raise original_call_error


# --- Hook Factory ---


def create_generic_hook(pillar: "Pillar", adapter: FrameworkAdapter) -> Callable:
    """
    Creates a generic hook function (sync or async) based on the provided adapter.
    The adapter instance dictates whether the returned hook is sync or async via adapter.is_async.
    """
    if not adapter or not isinstance(adapter, FrameworkAdapter):
        raise ValueError("Adapter must be an instance of FrameworkAdapter")

    is_async_hook = adapter.is_async

    if is_async_hook:
        # Define the wrapper hook that will be decorated
        async def async_hook_wrapper(wrapped: Callable, instance: Any, args: tuple, kwargs: dict) -> Any:
            """Async hook wrapper that calls the core implementation."""
            async with pillar.asession():
                return await _async_hook_implementation(pillar, adapter, wrapped, instance, args, kwargs)

        return async_hook_wrapper
    else:
        # Define the wrapper hook that will be decorated
        def sync_hook_wrapper(wrapped: Callable, instance: Any, args: tuple, kwargs: dict) -> Any:
            with pillar.session():
                """Sync hook wrapper that calls the core implementation."""
                return _sync_hook_implementation(pillar, adapter, wrapped, instance, args, kwargs)

        return sync_hook_wrapper
