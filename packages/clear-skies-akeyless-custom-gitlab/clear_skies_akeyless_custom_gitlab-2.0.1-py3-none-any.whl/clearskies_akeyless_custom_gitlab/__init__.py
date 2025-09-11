from typing import Any

import clearskies
import clearskies_akeyless_custom_producer
from clearskies import columns, validators

from clearskies_akeyless_custom_gitlab.create import create
from clearskies_akeyless_custom_gitlab.revoke import revoke
from clearskies_akeyless_custom_gitlab.rotate import rotate


class PayloadSchema(clearskies.Schema):
    """
    Schema defining the input parameters for the GitLab custom producer.

    This schema validates and documents the JSON payload sent to Akeyless for create, rotate, and revoke operations.

    Fields:
        id (int): Required. The ID of the GitLab group access token.
        personal_access_token (str): Required. Personal access token with permissions to manage group access tokens.
        group_id (int): Required. The GitLab group ID for which the token is managed.
        scopes (list[str]): Required. List of permission scopes for the token (default: ["read_api"]).
        access_level (int): Required. Access level for the token (default: 20, Reporter).
        api_url (str): Optional. Base URL for the GitLab API (default: "https://gitlab.com/api/v4").
        allowed_scopes (list[str]): Optional. List of allowed scopes for validation.
        allowed_group_ids (list[int]): Optional. List of allowed group IDs for validation.
    """

    id = columns.Integer(validators=[validators.Required()])

    personal_access_token = columns.String(validators=[validators.Required()])

    group_id = columns.Integer(validators=[validators.Required()])

    scopes = columns.Json(
        default=["read_api"],
        validators=[validators.Required()],
    )

    access_level = columns.Integer(
        default=20,  # 20 = Reporter
        validators=[validators.Required()],
    )

    api_url = columns.String(
        default="https://gitlab.com/api/v4",
    )

    allowed_scopes = columns.Json(default=[])

    allowed_group_ids = columns.Json(default=[])


class InputSchema(clearskies.Schema):
    """
    Schema defining additional input parameters for the GitLab custom producer.

    Fields:
        requested_group_id (int): Optional. The group ID requested for token operations.
        cache_id (str): Optional. An identifier for caching purposes.
        requested_scopes (list[str]): Optional. List of scopes requested for the token.
    """

    requested_group_id = columns.Integer()
    cache_id = columns.String()
    requested_scopes = columns.Json()


def build_clearskies_akeyless_custom_gitlab_producer(
    url: str = "",
) -> clearskies_akeyless_custom_producer.endpoints.NoInput:
    """
    Build and return a GitLab custom producer with create, rotate, and revoke endpoints.

    This function configures the producer for Akeyless, wiring up the endpoint handlers and schemas.

    Args:
        url (str): Optional URL prefix for the endpoints.

    Returns:
        clearskies_akeyless_custom_producer.endpoints.WithInput: The configured producer endpoint with input schema.
    """
    return clearskies_akeyless_custom_producer.endpoints.WithInput(
        create_callable=create,
        rotate_callable=rotate,
        revoke_callable=revoke,
        payload_schema=PayloadSchema,
        input_schema=InputSchema,
        url=url,
        id_column_name="id",
    )
