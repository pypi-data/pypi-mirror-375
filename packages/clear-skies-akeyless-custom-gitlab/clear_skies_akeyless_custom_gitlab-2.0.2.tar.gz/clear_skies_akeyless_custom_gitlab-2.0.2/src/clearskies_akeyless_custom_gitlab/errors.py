from typing import Any

from clearskies.exceptions import ClientError as ProducerError


class GitlabHostError(ProducerError):
    """Specific error response from Gitlab."""

    def __init__(self, api_url: str) -> None:
        super().__init__(f"{api_url} is not a valid Gitlab api endpoint.")


class GitlabError(ProducerError):
    """Specific error response from Gitlab."""

    def __init__(self, message: Any, api_url: str) -> None:
        super().__init__(f"Error message from Gitlab ({api_url}): {message}")


class GitlabProcessError(ProducerError):
    """Specific process error from Gitlab."""

    def __init__(self, message: Any, api_url: str) -> None:
        super().__init__(f"Unable to process the response from Gitlab ({api_url}): {message}")


class GitlabScopeError(ProducerError):
    """Specific process error from Gitlab."""

    def __init__(self, requested_scopes: list[str], allowed_scopes: list[str], api_url: str) -> None:
        super().__init__(
            f"Trying to get scope(s): {requested_scopes} that is not in allowed list: {allowed_scopes} from Gitlab ({api_url})"
        )


class GitlabGroupIdError(ProducerError):
    """Specific process error from Gitlab."""

    def __init__(self, requested_group_id: int, allowed_group_ids: list[int], api_url: str) -> None:
        super().__init__(
            f"Trying to get GAT for group: {requested_group_id} that is not in allowed list: {allowed_group_ids} from Gitlab ({api_url})"
        )


class GitlabTypeError(ProducerError):
    """Specific process error from Gitlab."""

    def __init__(self, argument: Any, requested_type: Any) -> None:
        super().__init__(
            f"Type error: trying to parse: {argument} of type {type(argument).__name__} must be {requested_type} )"
        )
