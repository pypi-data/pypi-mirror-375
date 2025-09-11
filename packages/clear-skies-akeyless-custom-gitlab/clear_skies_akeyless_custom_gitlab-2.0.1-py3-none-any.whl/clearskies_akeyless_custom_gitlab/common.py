from json import JSONDecodeError
from typing import Any

import requests

from clearskies_akeyless_custom_gitlab.errors import GitlabHostError


def verify_api_host(api_url: str, personal_access_token: str, requests: requests.Session) -> None:
    """Verify api url base is valid."""
    if api_url == "https://gitlab.com/api/v4":
        return
    response = requests.get(
        f"{api_url}/user",
        headers={"PRIVATE-TOKEN": personal_access_token},
    )
    try:
        response_data = response.json()
    except JSONDecodeError as e:
        raise GitlabHostError(api_url) from e

    if "username" not in response_data:
        raise GitlabHostError(api_url)
