"""
Main client class for the Pillar Python SDK.
"""

import asyncio
import logging
from collections.abc import Callable
from contextlib import asynccontextmanager, contextmanager
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import httpx
from pydantic import ValidationError

# Pillar
import pillar.context_vars as cv
from pillar.callbacks import (
    CallbackType,
    IsFlaggedCallable,
    OnFlaggedCallbackType,
    OnFlaggedResultType,
    _is_async_callable,
)
from pillar.errors import PillarAPIError, PillarRequestError, PillarTimeoutError, PillarValidationError
from pillar.interceptor.hooks.openai.patcher import _register_hooks_openai
from pillar.logging import Logger
from pillar.types import PillarApiRequest, PillarApiResponse, PillarMessage, PillarMetadata
from pillar.utils import _uri_validator


class Pillar:
    """
    Main client for the Pillar API.

    This class provides methods for interacting with the Pillar API,
    including session management and message checking.
    """

    _instance = None
    PROTECT_PATH = "/api/v1/protect"
    CLIENT_NAME = "python-sdk"

    def __init__(
        self,
        api_key: str,
        url: str = "https://api.pillar.security",
        timeout: float = 10.0,
        callbacks: list[CallbackType] | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
        logger: logging.Logger | None = None,
        disable_logging: bool = False,
        sync_client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        """
        Initialize a new Pillar client.

        Args:
            url: The URL of the Pillar API.
            api_key: Your Pillar API Key.
            timeout: HTTP request timeout in seconds, default 10 seconds.
            callbacks: List of callback functions to call on all requests,
                       can be sync or async, their signature must match the
                       expected signature of the callback functions,
                       they are being executed in the order they are added,
                       they are executed no matter the response status,
                       the return value of the callback functions is ignored.
            on_flagged_fn: Callback function to call when a request is blocked.
            is_flagged_fn: Block detection function to use, default is the one
                            provided by the Pillar SDK which check for response.action == "block".
            logger: Optional Python logging.Logger instance to log SDK operations.
                    If not provided, a default logger will be used.
            disable_logging: If True, completely disables all internal logging.
                             This overrides the logger parameter if both are provided.
            sync_client: Optional httpx.Client instance to use for sync requests.
            async_client: Optional httpx.AsyncClient instance to use for async requests.

        Raises:
            ValueError: If there is no API_KEY or the URL is invalid.
        """

        if not api_key:
            raise ValueError("API_KEY is required")

        if not _uri_validator(url):
            raise ValueError(f"Invalid url for pillar: {url}")

        # Initialize logger
        self.logger = Logger(self, logger if not disable_logging else None, disabled=disable_logging)

        try:
            self.version = version("pillar-security")
        except PackageNotFoundError:
            self.version = "unknown"

        # Validate provided clients
        if sync_client:
            if not isinstance(sync_client, httpx.Client):
                raise ValueError("sync_client must be an instance of httpx.Client")
            if not str(sync_client.base_url):
                raise ValueError(f"Please provide a base_url for sync_client: Client(base_url={url})")
        if async_client:
            if not isinstance(async_client, httpx.AsyncClient):
                raise ValueError("async_client must be an instance of httpx.AsyncClient")
            if not str(async_client.base_url):
                raise ValueError(f"Please provide a base_url for async_client: Client(base_url={url})")

        # Initialize HTTP clients, use provided clients if provided, otherwise create new ones
        self.client: httpx.Client = sync_client or httpx.Client(timeout=timeout, base_url=url)
        # aclient has None type for closing the client
        self.aclient: httpx.AsyncClient | None = async_client or httpx.AsyncClient(timeout=timeout, base_url=url)

        # update headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.client.headers.update(headers)
        self.aclient.headers.update(headers)

        # Initialize callbacks list
        self._callbacks: list[CallbackType] = callbacks or []

        if on_flagged_fn is not None:
            cv.pillar_on_flagged_fn.set(on_flagged_fn)
        else:
            self.logger.warning(f"No on_flagged_fn provided, using {cv.pillar_on_flagged_fn.name}")
        if is_flagged_fn is not None:
            cv.pillar_is_flagged_fn.set(is_flagged_fn)

        if Pillar._instance is not None:
            # For singleton warning, just use standard logging - this will be caught by pytest
            warning_msg = (
                "Pillar was initialized more than once. "
                "If using frameworks like Streamlit, "
                "cache the Pillar object to prevent multiple initializations."
            )
            logging.warning(warning_msg)
        else:
            # set instance
            Pillar._instance = self
            # register hooks
            self._register_hooks()

            client_summary = {
                "url": url,
                "number of custom callbacks": len(self._callbacks),
                "on_flagged_fn": cv.get_on_flagged_fn_name(),
                "sdk version": self.version,
                "sync client timeout": self.client.timeout,
                "async client timeout": self.aclient.timeout,
            }
            self.logger.info(f"Pillar client initialized with the following parameters: {client_summary}")

    # === Context Manager / Lifecycle ===

    def __enter__(self) -> "Pillar":
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> None:
        """Exit context manager, closing the client."""
        self.close()

    def __del__(self) -> None:
        """Clean up resources when the object is garbage collected."""
        try:
            if hasattr(self, "client") and self.client:
                self.close()
        except Exception as e:
            self.logger.warning(f"Error closing HTTP client: {e}")

    def close(self) -> None:
        """Explicitly close the HTTP client."""
        if hasattr(self, "client") and self.client:
            self.client.close()

    async def __aenter__(self) -> "Pillar":
        """Enter context manager."""
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any | None) -> None:
        """Exit context manager."""
        await self.aclose()

    async def aclose(self) -> None:
        """Explicitly close the HTTP client."""
        if hasattr(self, "aclient") and self.aclient:
            await self.aclient.aclose()

    # === Hook Registration ===

    def _register_hooks(self) -> None:
        """Register hooks for the client."""
        # LLM Provider Hooks
        _register_hooks_openai(self)
        # Context Hooks

    # === Callback Registration API ===

    def add_callback(self, callback: CallbackType) -> None:
        """
        Register a global callback function to call on all requests.

        Args:
            callback: A function to call on all requests.
                     Can be sync or async.
        """
        self._callbacks.append(callback)

    # === Callback Execution Helpers ===

    def _run_callbacks_sync(self, request: PillarApiRequest, response: PillarApiResponse) -> None:
        """Run all callbacks synchronously."""
        for cb in self._callbacks:
            try:
                if _is_async_callable(cb):
                    asyncio.run(cb(request, response))  # type: ignore[arg-type]
                else:
                    cb(request, response)
            except Exception as e:
                self.logger.error(f"Error in callback, callback name: {cb.__name__}, error: {e}")

    async def _run_callbacks_async(self, request: PillarApiRequest, response: PillarApiResponse) -> None:
        """Run all callbacks asynchronously."""
        for cb in self._callbacks:
            try:
                if _is_async_callable(cb):
                    await cb(request, response)  # type: ignore[misc]
                else:
                    cb(request, response)
            except Exception as e:
                self.logger.error(f"Error in callback, callback name: {cb.__name__}, error: {e}")

    def _is_flagged(self, response: PillarApiResponse) -> bool:
        """Detect if a response is blocked.

        Args:
            response: The response from Pillar to check.

        Returns:
            bool: True if the response is flagged, False otherwise.
        """
        dispatcher = cv.pillar_is_flagged_fn.get()
        if dispatcher is None:
            return False
        return dispatcher(response)

    def _handle_flagged_sync(self, request: PillarApiRequest, response: PillarApiResponse) -> OnFlaggedResultType:
        """Handle a blocked response synchronously.
        This method is called when the block detector returns True.
        It will raise an exception if the handler raises an exception.

        Args:
            request: The original request.
            response: The response for Pillar.

        Returns:
            List[PillarMessage]: The messages to pass to the LLM.
        Raises:
            PillarBlockError: If the handler raises an exception.
        """
        # This should not check the handler, it should just call it, _is_flagged should do that
        handler: OnFlaggedCallbackType = cv.pillar_on_flagged_fn.get()
        return handler(request, response)

    async def _handle_flagged_async(
        self, request: PillarApiRequest, response: PillarApiResponse
    ) -> OnFlaggedResultType:
        """Handle a blocked response asynchronously.
        This method is called when the block detector returns True.

        It will raise an exception if the handler raises an exception.
        Args:
            request: The original request.
            response: The response for Pillar.

        Returns:
            List[PillarMessage]: The messages to pass to the LLM.
        Raises:
            PillarBlockError: If the handler raises an exception.
        """
        # This should not check the handler, it should just call it, _is_flagged should do that
        handler: OnFlaggedCallbackType = cv.pillar_on_flagged_fn.get()
        return handler(request, response)

    # === Preparation Helper ===

    def _prepare_request(
        self,
        messages: list[PillarMessage],
        tools: list[dict[str, Any]] | None,
        provider: str | None,
        model: str | None,
        plr_persist: bool = True,
        plr_scanners: bool = True,
        plr_evidence: bool = True,
        plr_mask: bool = True,
    ) -> tuple[PillarApiRequest, dict[str, str]]:
        """Build the request data, headers, and resolve hooks for either sync or async."""
        if not messages:
            raise ValueError("Messages are required")

        metadata = PillarMetadata(
            source=self.CLIENT_NAME,
            version=self.version,
        )

        # Get the context variables for user_id and session_id
        user_id = cv.pillar_user_id.get()
        session_id = cv.pillar_session_id.get()

        # build the request data using PillarApiRequest dataclass
        request_data = PillarApiRequest(
            messages=messages,
            tools=tools,
            session_id=session_id,
            user_id=user_id,
            metadata=metadata,
            service=provider,
            model=model,
        )

        # build the headers
        headers = {
            "plr_persist": str(plr_persist).lower(),
            "plr_scanners": str(plr_scanners).lower(),
            "plr_evidence": str(plr_evidence).lower(),
            "plr_mask": str(plr_mask).lower(),
        }

        return request_data, headers

    # === HTTP I/O Helpers ===

    def _send_sync(
        self,
        request_data: PillarApiRequest,
        headers: dict[str, str],
    ) -> httpx.Response:
        """Issue a session POST, wrap any connection errors."""
        try:
            if self.client:
                return self.client.post(
                    self.PROTECT_PATH,
                    json=request_data.model_dump(),
                    headers=headers,
                )
            else:
                raise PillarRequestError("Client not initialized")
        except httpx.TimeoutException as e:
            self.logger.error(f"Reached timeout: {e}")
            raise PillarTimeoutError(f"Timeout: {e}") from e
        except httpx.RequestError as e:
            self.logger.error(f"Connection error: {e}")
            raise PillarRequestError(f"Connection error: {e}") from e

    async def _send_async(
        self,
        request_data: PillarApiRequest,
        headers: dict[str, str],
    ) -> httpx.Response:
        """Issue an async POST, wrap any connection errors."""
        try:
            if self.aclient:
                return await self.aclient.post(
                    self.PROTECT_PATH,
                    json=request_data.model_dump(),
                    headers=headers,
                )
            else:
                raise PillarRequestError("Async client not initialized")
        except httpx.TimeoutException as e:
            self.logger.error(f"Reached timeout: {e}")
            raise PillarTimeoutError(f"Timeout: {e}") from e
        except httpx.RequestError as e:
            self.logger.error(f"Connection error: {e}")
            raise PillarRequestError(f"Connection error: {e}") from e

    # === Response Processing Helpers ===
    def _process_sync(
        self,
        resp: httpx.Response,
        request_data: PillarApiRequest,
    ) -> OnFlaggedResultType:
        """
        Process a sync response from Pillar.

        Args:
            resp: The response from Pillar.
            request_data: The original request data.
        Returns:
            List[PillarMessage]: The messages to pass to the LLM.
        Raises:
            PillarBlockError: If the response is blocked and the on_flagged_fn raises an exception.
            PillarRequestError: If the request fails.
            PillarTimeoutError: If the request times out.
            PillarAPIError: If the response from Pillar is not valid.
        """

        # 1) validate response from Pillar
        if resp.status_code != 200:
            self.logger.error(f"Pillar API returned status code {resp.status_code}: {resp.text}")
            raise PillarAPIError(resp.status_code, resp.text)

        # 2) parse response
        try:
            data = resp.json()
            results = PillarApiResponse(**data)
        except ValidationError as e:
            self.logger.error(f"Pillar API Validation Error: {e.errors()}")
            raise PillarValidationError(e) from e

        # 3) callbacks (here also Pillar update context runs)
        self._run_callbacks_sync(request_data, results)

        # 4) detect flagged
        if self._is_flagged(results):
            self.logger.debug(f"Flagged detected, calling on_flagged_fn: {cv.get_on_flagged_fn_name()}")
            # may raise or return a fallback
            return self._handle_flagged_sync(request_data, results)

        # 5) return messages from the request
        return request_data.messages

    async def _process_async(
        self,
        resp: httpx.Response,
        request_data: PillarApiRequest,
    ) -> OnFlaggedResultType:
        """Process an async response from Pillar.

        Args:
            resp: The response from Pillar.
            request_data: The original request data.
        Returns:
            List[PillarMessage]: The messages to pass to the LLM.
        Raises:
            PillarBlockError: If the response is blocked and the on_flagged_fn raises an exception.
            PillarRequestError: If the request fails.
            PillarTimeoutError: If the request times out.
            PillarAPIError: If the response from Pillar is not valid.
        """

        # 1) validate response from Pillar
        if resp.status_code != 200:
            self.logger.error(f"Pillar API returned status code {resp.status_code}: {resp.text}")
            raise PillarAPIError(resp.status_code, resp.text)

        # 2) parse response
        try:
            data = resp.json()
            results = PillarApiResponse(**data)
        except ValidationError as e:
            self.logger.error(f"Pillar API Validation Error: {e.errors()}")
            raise PillarValidationError(e) from e

        # 3) callbacks
        await self._run_callbacks_async(request_data, results)

        # 4) detect flagged
        if self._is_flagged(results):
            self.logger.debug(f"Flagged detected, calling on_flagged_fn: {cv.get_on_flagged_fn_name()}")
            # may raise or return a fallback
            return await self._handle_flagged_async(request_data, results)

        # 5) return messages from the request
        return request_data.messages

    # === Public Analyze Methods ===

    def analyze_sync(
        self,
        messages: list[PillarMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        provider: str | None = None,
        model: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> OnFlaggedResultType:
        """
        Analyze a list of messages synchronously.

        Returns:
            List[PillarMessage]: The messages to pass to the LLM.
        Raises:
            PillarBlockError: If the response is blocked and the on_flagged_fn raises an exception.
            PillarRequestError: If the request fails.
            PillarTimeoutError: If the request times out.
            PillarAPIError: If the response from Pillar is not valid.
            PillarValidationError: If the response from Pillar is not valid.
        """
        on_flagged_fn = on_flagged_fn or cv.pillar_on_flagged_fn.get()
        is_flagged_fn = is_flagged_fn or cv.pillar_is_flagged_fn.get()
        request_data, headers = self._prepare_request(messages, tools, provider, model)
        resp = self._send_sync(request_data, headers)
        return self._process_sync(resp, request_data)

    async def analyze_async(
        self,
        messages: list[PillarMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        provider: str | None = None,
        model: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> OnFlaggedResultType:
        """
        Analyze a list of messages asynchronously.

        Returns:
            List[PillarMessage]: The messages to pass to the LLM.
        Raises:
            PillarBlockError: If the response is blocked and the on_flagged_fn raises an exception.
            PillarRequestError: If the request fails.
            PillarTimeoutError: If the request times out.
            PillarAPIError: If the response from Pillar is not valid.
            PillarValidationError: If the response from Pillar is not valid.
        """
        on_flagged_fn = on_flagged_fn or cv.pillar_on_flagged_fn.get()
        is_flagged_fn = is_flagged_fn or cv.pillar_is_flagged_fn.get()
        request_data, headers = self._prepare_request(messages, tools, provider, model)
        resp = await self._send_async(request_data, headers)
        return await self._process_async(resp, request_data)

    # === Session Scoping Contexts ===

    def with_session(
        self,
        pillar_user_id: str | None = None,
        pillar_session_id: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator for a function to run within a sync session context.

        The session context is used to store the:
          - session_id
          - user_id
          - on_flagged_fn
          - is_flagged_fn

        Args:
            pillar_user_id: User identifier.
            pillar_session_id: Session identifier. If not provided, one will be generated.
            on_flagged_fn: Callback function for blocked requests
                        If not provided, try context variables, then instance defaults.
            is_flagged_fn: Custom block detection function
                              If not provided, try context variables, then instance defaults.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # sync wrapper
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.session(
                    pillar_user_id,
                    pillar_session_id,
                    on_flagged_fn,
                    is_flagged_fn,
                ):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def with_asession(
        self,
        pillar_user_id: str | None = None,
        pillar_session_id: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator for a function to run within an async session context.

        The session context is used to store the:
          - session_id
          - user_id
          - on_flagged_fn
          - is_flagged_fn

        Args:
            pillar_user_id: User identifier.
            pillar_session_id: Session identifier. If not provided, one will be generated.
            on_flagged_fn: Callback function for blocked requests
                        If not provided, try context variables, then instance defaults.
            is_flagged_fn: Custom block detection function
                              If not provided, try context variables, then instance defaults.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # async wrapper
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                async with self.asession(
                    pillar_user_id,
                    pillar_session_id,
                    on_flagged_fn,
                    is_flagged_fn,
                ):
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @contextmanager
    def session(
        self,
        pillar_user_id: str | None = None,
        pillar_session_id: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> Any:
        """
        Context manager for a Pillar session.

        Sets the:
          - session_id
          - user_id
        in the context variables.
        When entering the context manager, session variables are saved.
        When exiting, the previous context is restored.

        Args:
            pillar_user_id: User identifier.
            pillar_session_id: Session identifier. If not provided, one will be generated.

        Example:
            ```python
            with pillar.session(pillar_user_id="user123"):
                # Code that will run in the context of this session with the specified parameters
                completion = openai_client.chat.completions.create(...)
            ```
        """
        with self._session_context(
            pillar_user_id=pillar_user_id,
            pillar_session_id=pillar_session_id,
            on_flagged_fn=on_flagged_fn,
            is_flagged_fn=is_flagged_fn,
        ):
            yield

    @asynccontextmanager
    async def asession(
        self,
        pillar_user_id: str | None = None,
        pillar_session_id: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> Any:
        """
        Async context manager for a Pillar session.

        Sets the:
          - session_id
          - user_id
          - on_flagged_fn
          - is_flagged_fn
        in the context variables.
        When entering the context manager, session variables are saved.
        When exiting, the previous context is restored.

        Args:
            pillar_user_id: User identifier.
            pillar_session_id: Session identifier. If not provided, one will be generated.
            on_flagged_fn: Callback function for blocked requests
                        If not provided, try context variables, then instance defaults.
            is_flagged_fn: Custom block detection function
                              If not provided, try context variables, then instance defaults.

        Example:
            ```python
            async with pillar.asession(pillar_user_id="user123"):
                # Code that will run in the context of this session with the specified parameters
                completion = openai_client.chat.completions.create(...)
            ```
        """
        async with self._async_session_context(
            pillar_user_id=pillar_user_id,
            pillar_session_id=pillar_session_id,
            on_flagged_fn=on_flagged_fn,
            is_flagged_fn=is_flagged_fn,
        ):
            yield

    @contextmanager
    def _session_context(
        self,
        pillar_user_id: str | None = None,
        pillar_session_id: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> Any:
        """
        Context manager for a Pillar session.

        Sets the:
          - session_id
          - user_id
          - on_flagged_fn
          - is_flagged_fn
        in the context variables.
        When entering the context manager, session variables are saved.
        When exiting, the previous context is restored.

        Args:
            pillar_user_id: User identifier. If not provided, one will be generated.
            pillar_session_id: Session identifier. If not provided, one will be generated.
            on_flagged_fn: Callback function for blocked requests
                        If not provided, try context variables, then instance defaults.
            is_flagged_fn: Custom block detection function
                              If not provided, try context variables, then instance defaults.
        """

        # Get the tokens, which will be used to restore the context
        session_id_token = cv.session_id_token(pillar_session_id)
        user_id_token = cv.user_id_token(pillar_user_id)
        on_flagged_fn_token = cv.on_flagged_fn_token(on_flagged_fn)
        is_flagged_fn_token = cv.is_flagged_fn_token(is_flagged_fn)

        try:
            yield
        finally:
            # restore previous context
            cv.pillar_session_id.reset(session_id_token)
            cv.pillar_user_id.reset(user_id_token)
            cv.pillar_on_flagged_fn.reset(on_flagged_fn_token)
            cv.pillar_is_flagged_fn.reset(is_flagged_fn_token)

    @asynccontextmanager
    async def _async_session_context(
        self,
        pillar_user_id: str | None = None,
        pillar_session_id: str | None = None,
        on_flagged_fn: OnFlaggedCallbackType | None = None,
        is_flagged_fn: IsFlaggedCallable | None = None,
    ) -> Any:
        """
        Context manager for a Pillar session.

        Sets the:
          - session_id
          - user_id
          - on_flagged_fn
          - is_flagged_fn
        in the context variables.
        When entering the context manager, session variables are saved.
        When exiting, the previous context is restored.

        Args:
            pillar_user_id: User identifier. If not provided, one will be generated.
            pillar_session_id: Session identifier. If not provided, one will be generated.
            on_flagged_fn: Callback function for blocked requests
                        If not provided, try context variables, then instance defaults.
            is_flagged_fn: Custom block detection function
                              If not provided, try context variables, then instance defaults.
        """

        # Get the tokens, which will be used to restore the context
        session_id_token = cv.session_id_token(pillar_session_id)
        user_id_token = cv.user_id_token(pillar_user_id)
        on_flagged_fn_token = cv.on_flagged_fn_token(on_flagged_fn)
        is_flagged_fn_token = cv.is_flagged_fn_token(is_flagged_fn)

        try:
            yield
        finally:
            # restore previous context
            cv.pillar_session_id.reset(session_id_token)
            cv.pillar_user_id.reset(user_id_token)
            cv.pillar_on_flagged_fn.reset(on_flagged_fn_token)
            cv.pillar_is_flagged_fn.reset(is_flagged_fn_token)

    # === Logging ===

    def set_logger(self, logger: logging.Logger | None = None, disable_logging: bool = False) -> None:
        """
        Set or update the logger for this Pillar instance.

        Args:
            logger: A Python logging.Logger instance to receive SDK logs,
                   or None to disable custom logging.
            disable_logging: If True, completely disables all internal logging.
                             This overrides the logger parameter if both are provided.
        """
        if disable_logging:
            self.logger.disable()
            return

        self.logger.enable()
        self.logger.set_logger(logger)
        if logger:
            logger.debug("Pillar logger successfully attached")

    def _log(self, level: int, message: str, trace: str | None = None, **kwargs) -> None:
        """
        Internal method to log a message to the Pillar system.
        This is used by the Logger class.

        In the future, this will also send important logs to the Pillar API.
        """
        pass
