import datetime
from typing import Any

import clearskies
import requests

from clearskies_akeyless_custom_gitlab.common import verify_api_host
from clearskies_akeyless_custom_gitlab.errors import (
    GitlabError,
    GitlabGroupIdError,
    GitlabProcessError,
    GitlabScopeError,
    GitlabTypeError,
)


def create(
    group_id: int,
    personal_access_token: str,
    scopes: list[str],
    access_level: int,
    requests: requests.Session,
    uuid: Any,
    utcnow: datetime.datetime,
    for_rotate: bool = False,
    allowed_scopes: list[str] = [],
    requested_scopes: list[str] | None = None,
    allowed_group_ids: list[int] = [],
    requested_group_id: int | None = None,
    api_url: str = "https://gitlab.com/api/v4",
) -> dict[str, Any]:
    """
    Create a GitLab Group Access Token (GAT) for the specified group.

    Args:
        group_id (int): The GitLab group ID for which to create the access token.
        personal_access_token (str): Personal access token with permissions to create group access tokens.
        scopes (list[str]): List of permission scopes for the token (e.g., ['read_api', 'write_repository']).
        access_level (int): Access level for the token (e.g., 30 for Developer).
        requests (requests.Session): HTTP session for making API calls.
        uuid (Any): UUID generator, used to create a unique token name.
        utcnow (datetime.datetime): Current UTC datetime, used for token expiration.
        for_rotate (bool, optional): If True, indicates the call is for rotation. Default is False.
        allowed_scopes (list[str], optional): List of allowed scopes. Default is [].
        requested_scopes (list[str], optional): List of requested scopes. Default is [].
        allowed_group_ids (list[int], optional): List of allowed group IDs. Default is [].
        requested_group_id (int | None, optional): Requested group ID. Default is None.
        api_url (str, optional): Base URL for the GitLab API. Default is "https://gitlab.com/api/v4".

    Returns:
        dict[str, Any]: Dictionary containing:
            - 'id': Composite ID including the token ID and group ID.
            - 'group_access_token': The created group access token string.

    Raises:
        GitlabTypeError: If allowed_scopes, requested_scopes, or allowed_group_ids are not lists.
        GitlabScopeError: If requested scopes are not allowed.
        GitlabGroupIdError: If requested group ID is not allowed.
        GitlabError: If the GitLab API returns an error or message.
        GitlabProcessError: If the response does not contain a token.
    """
    verify_api_host(api_url, personal_access_token, requests)

    if not isinstance(allowed_scopes, list):
        raise GitlabTypeError("allowed_scopes", "list[string]")
    if not isinstance(requested_scopes, list):
        raise GitlabTypeError("requested_scopes", "list[string]")
    if not isinstance(allowed_group_ids, list):
        raise GitlabTypeError("allowed_group_ids", "list[int]")

    if allowed_scopes and requested_scopes:
        # check if there are scopes defined that are now allowed.
        not_allowed = list(set(requested_scopes).difference(allowed_scopes))
        if not_allowed:
            raise GitlabScopeError(not_allowed, allowed_scopes, api_url)
        scopes = requested_scopes
    if allowed_group_ids and requested_group_id:
        if requested_group_id not in allowed_group_ids:
            raise GitlabGroupIdError(requested_group_id, allowed_group_ids, api_url)
        else:
            group_id = requested_group_id

    response = requests.post(
        f"{api_url}/groups/{group_id}/access_tokens",
        json={
            "name": "akeyless-" + str(uuid.uuid4()),
            "scopes": scopes,
            "access_level": access_level,
            "expires_at": (utcnow + datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
        },
        headers={"PRIVATE-TOKEN": personal_access_token, "content-type": "application/json"},
    )
    if not response.ok:
        raise GitlabError(response.text, api_url)
    response_data = response.json()
    if "message" in response_data:
        raise GitlabError(response_data["message"], api_url)
    if "token" not in response_data:
        raise GitlabProcessError(response_data, api_url)

    """
    We  need to change the id because the revocation needs to know not just the id of the GAT,
    but also what group it belongs to.  Since we can let people request a GAT for a
    different group, we need to record the group id in the id we return to Akeyless.
    """
    return {
        "id": f"{response_data['id']}_group_id_{group_id}",
        "group_access_token": response_data["token"],
    }
