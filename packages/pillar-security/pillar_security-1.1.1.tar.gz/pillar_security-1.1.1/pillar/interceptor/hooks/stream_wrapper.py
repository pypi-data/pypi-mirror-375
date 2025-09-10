import traceback
from collections.abc import AsyncIterable, Callable, Iterable
from typing import TYPE_CHECKING, Any

from pillar.context_vars import ContextObject
from pillar.interceptor.hooks.framework_adapter import ExtractedInput
from pillar.types import PillarMessage

if TYPE_CHECKING:
    from pillar.client import Pillar

# --- Synchronous Stream Analyzer ---


class SyncStreamAnalyzer(Iterable):
    """
    Wraps a sync iterable (like OpenAI's sync Stream) to support
    sync context management (__enter__, __exit__) while allowing
    post-iteration analysis.

    it is a wrapper around the original stream result,
    it is used to analyze the stream result after it is consumed.
    """

    def __init__(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,
        original_stream: Iterable[Any],
        collector_func: Callable[[list[Any]], list[PillarMessage]],
        provider_name: str,
        previous_context: ContextObject,
    ):
        self._pillar = pillar
        self._extracted_input = extracted_input
        self._original_stream = original_stream
        self._collector_func = collector_func
        self._provider_name = provider_name
        self._chunks: list[Any] = []
        self._iterator = None  # Store the iterator obtained from __iter__
        self._previous_context = previous_context

    def _error(
        self,
        message: str,
    ):
        self._pillar.logger.error(f"SyncStreamAnalyzer: {message}")

    def __enter__(self):
        """Enter the sync context."""
        # Delegate to original stream if it supports context management
        if hasattr(self._original_stream, "__enter__"):
            self._original_stream.__enter__()
        # Get the iterator here to ensure it's ready for __next__
        self._iterator = self._original_stream.__iter__()
        return self  # Return self to be used in 'as stream'

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the sync context and perform analysis."""
        analysis_exception = None
        try:
            session_id = self._previous_context.pillar_session_id
            user_id = self._previous_context.pillar_user_id
            is_flagged_fn = self._previous_context.is_flagged_fn
            on_flagged_fn = self._previous_context.on_flagged_fn

            with self._pillar.session(
                pillar_session_id=session_id,
                pillar_user_id=user_id,
                is_flagged_fn=is_flagged_fn,
                on_flagged_fn=on_flagged_fn,
            ):
                # Perform analysis after stream is consumed (or context exited)
                messages = self._collector_func(self._chunks)
                if messages:
                    analyze_kwargs = {
                        "messages": messages,
                        "model": self._extracted_input.model,
                        "provider": self._provider_name,
                        "tools": self._extracted_input.tools,
                    }
                    # Call the sync analyze function
                    self._pillar.analyze_sync(**analyze_kwargs)
        except Exception as e:
            analysis_exception = e
            self._error(f"Exception during analysis: {e}")
            self._error(traceback.format_exc())

        # Reset iterator state
        self._iterator = None

        # Delegate to original stream's exit if it exists
        original_exit_result = True  # Default: Don't suppress exceptions
        if hasattr(self._original_stream, "__exit__"):
            # Propagate exception info
            original_exit_result = self._original_stream.__exit__(exc_type, exc_val, exc_tb)

        if analysis_exception:
            if exc_type is None:
                raise analysis_exception
            else:
                self._error(f"Analysis failed after another exception: {analysis_exception}")

        # Return the result of the original __exit__ (or True if no original)
        # False suppresses exceptions from the 'with' block, True propagates them.
        # Careful: if original_exit_result is None (common default), treat as True.
        return original_exit_result if original_exit_result is not None else True

    def __iter__(self):
        """Return the sync iterator."""
        if self._iterator is None:
            self._iterator = self._original_stream.__iter__()
        return self

    def __next__(self):
        """Get the next item from the stream."""
        if self._iterator is None:
            self._iterator = self._original_stream.__iter__()
        try:
            chunk = next(self._iterator)
            self._chunks.append(chunk)
            return chunk
        except StopIteration as e:
            raise e
        except Exception as e:
            self._error(f"Exception during iteration: {e}")
            self._error(traceback.format_exc())
            raise e


# --- Async Stream Analyzer ---


class AsyncStreamAnalyzer(AsyncIterable):
    """
    Wraps an async iterable (like OpenAI's AsyncStream) to support
    async context management (__aenter__, __aexit__) while allowing
    post-iteration analysis.

    it is a wrapper around the original stream result,
    it is used to analyze the stream result after it is consumed.
    """

    def __init__(
        self,
        pillar: "Pillar",
        extracted_input: ExtractedInput,
        original_stream: AsyncIterable[Any],
        collector_func: Callable[[list[Any]], list[PillarMessage]],
        provider_name: str,
        previous_context: ContextObject,
    ):
        self._pillar = pillar
        self._extracted_input = extracted_input
        self._original_stream = original_stream
        self._collector_func = collector_func
        self._provider_name = provider_name
        self._chunks: list[Any] = []
        self._iterator = None  # Store the iterator obtained from __iter__
        self._previous_context = previous_context

    def _error(
        self,
        message: str,
    ):
        self._pillar.logger.error(f"AsyncStreamAnalyzer: {message}")

    async def __aenter__(self):
        """Enter the async context."""
        # Delegate to original stream if it supports context management
        if hasattr(self._original_stream, "__aenter__"):
            await self._original_stream.__aenter__()
        # Get the iterator here to ensure it's ready for __anext__
        self._iterator = self._original_stream.__aiter__()
        return self  # Return self to be used in 'as response'

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context and perform analysis."""
        analysis_exception = None
        try:
            session_id = self._previous_context.pillar_session_id
            user_id = self._previous_context.pillar_user_id
            async with self._pillar.asession(pillar_session_id=session_id, pillar_user_id=user_id):
                # Perform analysis after stream is consumed (or context exited)
                messages = self._collector_func(self._chunks)
                if messages:
                    analyze_kwargs = {
                        "messages": messages,
                        "model": self._extracted_input.model,
                        "provider": self._provider_name,
                        "tools": self._extracted_input.tools,
                    }
                    await self._pillar.analyze_async(**analyze_kwargs)
        except Exception as e:
            analysis_exception = e  # Store analysis exception
            self._error(f"Exception during analysis: {e}")
            self._error(traceback.format_exc())
            raise e from None

        # Reset iterator state
        self._iterator = None

        # Delegate to original stream's exit if it exists
        original_exit_result = True  # Default if no original __aexit__
        if hasattr(self._original_stream, "__aexit__"):
            # Propagate exception info if any occurred during iteration/context
            original_exit_result = await self._original_stream.__aexit__(exc_type, exc_val, exc_tb)

        # If analysis failed, ensure the exception is propagated unless
        # the original __aexit__ suppressed an existing exception.
        if analysis_exception:
            if exc_type is None:  # No exception from 'with' block
                raise analysis_exception  # Raise the analysis exception
            else:
                # An exception already occurred in the 'with' block or original __aexit__.
                # Log the analysis exception but let the original exception propagate.
                self._error(f"Analysis failed after another exception: {analysis_exception}")

        # Return the result of the original __aexit__ (or True)
        # This determines if exceptions from the 'with' block are suppressed
        return original_exit_result

    def __aiter__(self):
        """Return the async iterator."""
        # Ensure iterator is obtained if not already done in __aenter__
        if self._iterator is None:
            self._iterator = self._original_stream.__aiter__()
        return self  # The wrapper itself is the async iterator

    async def __anext__(self):
        """Get the next item from the stream."""
        if self._iterator is None:
            # This might happen if __aiter__ is called before __aenter__
            # or after __aexit__.
            self._iterator = self._original_stream.__aiter__()

        try:
            # Get the next chunk from the original stream's iterator
            chunk = await self._iterator.__anext__()
            # Store the chunk for later analysis
            self._chunks.append(chunk)
            # Yield the chunk to the consumer (LangChain)
            return chunk
        except StopAsyncIteration as e:
            # Original stream is exhausted
            raise e
        except Exception as e:
            self._error(f"Exception during iteration: {e}")
            self._error(traceback.format_exc())
            raise e
