from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, NamedTuple

from pillar.logging import Logger as PillarLogger

if TYPE_CHECKING:
    from pillar.client import Pillar


class ContextData(NamedTuple):
    """Standardized structure for context data extracted from framework calls."""

    context_id: str | None  # The main context identifier (e.g., run_id, session_id)
    is_root: bool  # Whether this is a root context (e.g., root run)
    original_kwargs: dict  # Keep original kwargs for fallback/reconstruction


class ContextFrameworkAdapter(ABC):
    """
    Abstract Base Class defining the interface for context-specific hook logic.
    """

    _is_async: bool  # Internal flag set during instantiation

    def __init__(self, is_async: bool, logger: PillarLogger):
        self._is_async = is_async
        self.logger = logger

    @property
    def is_async(self) -> bool:
        """Returns True if the adapter is configured for asynchronous operations."""
        return self._is_async

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'langsmith', 'langchain')."""
        pass

    @abstractmethod
    def extract_context(self, run_obj: Any, args: tuple, kwargs: dict) -> ContextData:
        """
        Extract relevant context information from the framework's specific function arguments.
        Should populate all fields of ContextData.
        Raises ValueError if essential arguments are missing.

        run_obj is the object returned by the framework's function.
        args is the tuple of arguments passed to the framework's function.
        kwargs is the dictionary of keyword arguments passed to the framework's function.
        """
        pass

    @abstractmethod
    def process_context(self, pillar: "Pillar", context_data: ContextData) -> None:
        """
        Process the extracted context data and update Pillar's context accordingly.
        For sync operations.
        """
        pass

    @abstractmethod
    async def process_context_async(self, pillar: "Pillar", context_data: ContextData) -> None:
        """
        Process the extracted context data and update Pillar's context accordingly.
        For async operations.
        """
        pass
