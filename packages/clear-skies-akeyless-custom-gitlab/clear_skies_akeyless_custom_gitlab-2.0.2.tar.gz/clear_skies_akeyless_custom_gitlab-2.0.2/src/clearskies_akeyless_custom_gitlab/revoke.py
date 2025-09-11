from typing import Any

import clearskies
import requests

from clearskies_akeyless_custom_gitlab.common import verify_api_host
from clearskies_akeyless_custom_gitlab.errors import GitlabError


def revoke(
    id_to_delete: str | int,
    personal_access_token: str,
    requests: requests.Session,
    api_url: str = "https://gitlab.com/api/v4",
) -> None:
    """
    Revoke a GitLab group access token for the specified group and token ID.

    Args:
        id_to_delete (str | int): The ID of the group access token to revoke. May include group ID as a suffix.
        personal_access_token (str): Personal access token with permissions to revoke group access tokens.
        requests (requests.Session): HTTP session for making API calls.
        api_url (str, optional): Base URL for the GitLab API. Default is "https://gitlab.com/api/v4".

    Returns:
        None

    Raises:
        GitlabError: If the GitLab API returns an error or the revocation fails.
    """
    verify_api_host(api_url, personal_access_token, requests)

    """
    Since we can let people request a GAT for a different group, we need to extract the group id and the actual id
    in the id we retrieve from Akeyless.
    """
    if "_group_id_" not in str(id_to_delete):
        raise GitlabError(f"Invalid id format for revocation: {id_to_delete}", api_url)

    [id_to_delete, group_id] = str(id_to_delete).split("_group_id_")

    response = requests.delete(
        f"{api_url}/groups/{group_id}/access_tokens/{id_to_delete}",
        headers={"PRIVATE-TOKEN": personal_access_token},
    )
    if not response.ok:
        raise GitlabError(response.text, api_url)
