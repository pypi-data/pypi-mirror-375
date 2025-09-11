import logging
from typing import Any

import clearskies
import requests

from clearskies_akeyless_custom_gitlab.common import verify_api_host
from clearskies_akeyless_custom_gitlab.errors import GitlabError

logger = logging.getLogger(__name__)


def rotate(
    id: int,
    personal_access_token: str,
    payload: dict[str, Any],
    requests: requests.Session,
    api_url: str = "https://gitlab.com/api/v4",
) -> dict[str, Any]:
    """
    Rotate a GitLab personal access token for the specified token ID.

    Args:
        id (int): The ID of the personal access token to rotate.
        personal_access_token (str): Personal access token with permissions to rotate tokens.
        payload (dict[str, Any]): Additional data to include in the returned dictionary.
        requests (requests.Session): HTTP session for making API calls.
        api_url (str, optional): Base URL for the GitLab API. Default is "https://gitlab.com/api/v4".

    Returns:
        dict[str, Any]: Dictionary containing:
            - All key-value pairs from the input payload.
            - 'id': The ID of the rotated personal access token.
            - 'personal_access_token': The new personal access token string.

    Raises:
        GitlabError: If the GitLab API returns an error or the rotation fails.
    """
    verify_api_host(api_url, personal_access_token, requests)
    response = requests.post(
        f"{api_url}/personal_access_tokens/self/rotate",
        headers={"PRIVATE-TOKEN": personal_access_token},
    )
    if not response.ok:
        # Fallback to rotating a specific token if self-rotate fails
        logger.warning("Self-rotate failed, attempting to rotate specific token ID")
        response = requests.post(
            f"{api_url}/personal_access_tokens/{id}/rotate",
            headers={"PRIVATE-TOKEN": personal_access_token},
        )
        if not response.ok:
            raise GitlabError(response.text, api_url)

    response_data = response.json()
    return {
        **payload,
        "id": response_data["id"],
        "personal_access_token": response_data["token"],
    }
