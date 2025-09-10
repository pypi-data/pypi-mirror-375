from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from packaging.version import parse as parse_version
from wrapt import wrap_function_wrapper

if TYPE_CHECKING:
    from pillar.client import Pillar

# Import the factory from its new location
from pillar.interceptor.hooks.openai.adapter import OpenAIAPIType, create_openai_hook_factory


def _patch_openai_v0(pillar_client: "Pillar"):
    """Applies patches for OpenAI SDK < 1.0.0."""
    # Only sync APIs existed
    # -- ChatCompletion --
    wrap_function_wrapper(
        "openai",
        "ChatCompletion.create",
        create_openai_hook_factory(
            pillar=pillar_client,
            is_async=False,
            api_type=OpenAIAPIType.CHAT,
        ),
    )
    # -- Completion --
    wrap_function_wrapper(
        "openai",
        "Completion.create",
        create_openai_hook_factory(
            pillar=pillar_client,
            is_async=False,
            api_type=OpenAIAPIType.COMPLETION,
        ),
    )
    pillar_client.logger.debug("Registered OpenAI hooks (< 1.0.0)")


def _patch_openai_v1(pillar_client: "Pillar"):
    """Applies patches for OpenAI SDK >= 1.0.0 and < 2.0.0."""
    # Both sync and async APIs
    # -- ChatCompletion API --
    wrap_function_wrapper(
        "openai.resources.chat.completions",
        "Completions.create",
        create_openai_hook_factory(
            pillar=pillar_client,
            is_async=False,
            api_type=OpenAIAPIType.CHAT,
        ),
    )
    wrap_function_wrapper(
        "openai.resources.chat.completions",
        "AsyncCompletions.create",
        create_openai_hook_factory(
            pillar=pillar_client,
            is_async=True,
            api_type=OpenAIAPIType.CHAT,
        ),
    )
    # -- Completion API --
    wrap_function_wrapper(
        "openai.resources.completions",
        "Completions.create",
        create_openai_hook_factory(
            pillar=pillar_client,
            is_async=False,
            api_type=OpenAIAPIType.COMPLETION,
        ),
    )
    wrap_function_wrapper(
        "openai.resources.completions",
        "AsyncCompletions.create",
        create_openai_hook_factory(
            pillar=pillar_client,
            is_async=True,
            api_type=OpenAIAPIType.COMPLETION,
        ),
    )
    pillar_client.logger.debug("Registered OpenAI v1 hooks (>= 1.0.0, < 2.0.0)")


def _register_hooks_openai(pillar_client: "Pillar") -> None:
    """
    Register OpenAI hooks using a factory pattern.
    Handles different SDK versions by dispatching to specific patching functions.
    """
    try:
        raw_openai_version = version("openai")
        parsed_openai_version = parse_version(raw_openai_version)
        # Define version boundaries
        v1_0_0 = parse_version("1.0.0")
        v2_0_0 = parse_version("2.0.0")

    except PackageNotFoundError:
        pillar_client.logger.debug("OpenAI package not found. Skipping hooks.")
        return
    except Exception as e:
        pillar_client.logger.error(f"Could not parse OpenAI version: {e}")
        return

    try:
        if parsed_openai_version < v1_0_0:
            # === Legacy OpenAI SDK (<1.0.0) ===
            _patch_openai_v0(pillar_client)
        elif v1_0_0 <= parsed_openai_version < v2_0_0:
            # === Modern OpenAI SDK (>=1.0.0, < 2.0.0) ===
            _patch_openai_v1(pillar_client)
        else:
            # === Unsupported/Future OpenAI SDK (>=2.0.0) ===
            pillar_client.logger.warning(
                f"OpenAI version {raw_openai_version} (>= 2.0.0) "
                "is not explicitly supported by Pillar hooks. "
                "Attempting v1 patching, but compatibility is not guaranteed."
            )
            # Optionally, attempt modern v1 patching as a fallback or do nothing
            try:
                _patch_openai_v1(pillar_client)
            except Exception as f_e:
                pillar_client.logger.error(f"Failed to apply fallback patching for OpenAI {raw_openai_version}: {f_e}")

    except Exception as e:
        pillar_client.logger.error(
            f"Failed to register OpenAI hooks for version {raw_openai_version}: {e}", exc_info=True
        )
