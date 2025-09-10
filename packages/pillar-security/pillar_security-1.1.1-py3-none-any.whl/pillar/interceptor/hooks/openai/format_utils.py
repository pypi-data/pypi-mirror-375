from pillar.callbacks import OnFlaggedResultType
from pillar.types import PillarMessage

KNOWN_ROLE_PREFIXES = ("System:", "Human:", "Assistant:")


def parse_completion_to_pillar_messages(input: str | list[str]) -> list[PillarMessage]:
    """
    Convert a LangChain-style flattened prompt (e.g. ['System:...\nHuman:...'])
    into a list of PillarMessage objects.
    """
    if isinstance(input, str):
        input_str = input.strip()
    elif isinstance(input, list):
        # If the input is a list, join the list into a single string
        input_str = "\n".join(input).strip()

    # Define known role mappings
    role_map = {
        "System": "system",
        "Human": "user",
        "Assistant": "assistant",
    }

    default_role = "user"

    messages = []
    current_role = None
    current_content = []

    # Split into lines and process line by line
    for line in input_str.splitlines():
        stripped_line = line.strip()

        # Detect a new role marker
        if any(stripped_line.startswith(r + ":") for r in role_map):
            # If there was an ongoing message, finalize it
            if current_role:
                messages.append(PillarMessage(role=current_role, content="\n".join(current_content).strip()))

            # Extract the role and start a new message
            role_label, _, rest = stripped_line.partition(":")
            current_role = role_map.get(role_label.strip())
            current_content = [rest.strip()] if rest.strip() else []
        else:
            # Continuation of current message
            current_content.append(stripped_line)

    # Final message
    if current_role:
        messages.append(PillarMessage(role=current_role, content="\n".join(current_content).strip()))
    # If no role was detected but there is content, assume default role
    elif not messages and current_content:
        messages.append(
            PillarMessage(
                role=default_role,  # Use the predefined default_role
                content="\n".join(current_content).strip(),
            )
        )

    return messages


def pillar_messages_to_completion(messages: OnFlaggedResultType, had_role_prefix: bool) -> str:
    """
    Convert a list of PillarMessage objects into a flattened prompt string
    using LangChain-style role prefixes (System:, Human:, Assistant:).
    """
    if isinstance(messages, list):
        pass
    elif isinstance(messages, dict):
        messages = [PillarMessage(**messages)]
    else:
        raise ValueError(f"Invalid messages type: {type(messages)}")

    role_prefix = {
        "system": "System",
        "user": "Human",
        "assistant": "Assistant",
    }

    parts = []

    for msg in messages:
        # Skip tool-only messages with no content
        if msg.content is None:
            continue

        # Format each message with its role prefix
        if had_role_prefix:
            prefix = role_prefix.get(msg.role, msg.role.capitalize())
            parts.append(f"{prefix}: {msg.content.strip()}")
        else:
            parts.append(f"{msg.content.strip()}")

    return "\n".join(parts)
