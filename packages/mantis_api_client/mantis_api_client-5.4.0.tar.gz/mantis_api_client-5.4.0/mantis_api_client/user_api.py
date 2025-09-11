#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

import requests

from mantis_api_client.config import mantis_api_client_config
from mantis_api_client.oidc import authorize

# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: Any) -> requests.Response:
    return requests.get(
        f"{mantis_api_client_config.user_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        **kwargs,
    )


def _post(route: str, **kwargs: Any) -> requests.Response:
    return requests.post(
        f"{mantis_api_client_config.user_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        **kwargs,
    )


def _put(route: str, **kwargs: Any) -> requests.Response:
    return requests.put(
        f"{mantis_api_client_config.user_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        **kwargs,
    )


def _delete(route: str, **kwargs: Any) -> requests.Response:
    return requests.delete(
        f"{mantis_api_client_config.user_api_url}{route}",
        verify=mantis_api_client_config.cacert,
        cert=(mantis_api_client_config.cert, mantis_api_client_config.key),
        **kwargs,
    )


def _handle_error(
    result: requests.Response, context_error_msg: str
) -> requests.Response:
    error_msg = ""
    if result.headers.get("content-type") == "application/json":
        error_data = result.json()
        for k in ("message", "detail"):
            if k in error_data:
                error_msg = error_data[k]
                break
    if not error_msg:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """
    Return User API version.

    :return: The version number is a string
    """
    result = authorize(_get)("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve User API version")

    return result.json()


# -------------------------------------------------------------------------- #
# User API (users)
# -------------------------------------------------------------------------- #


# def fetch_users() -> Any:
#     """Fetch users of the current organization."""
#     result = authorize(_get)("/users")

#     if result.status_code != 200:
#         _handle_error(result, "Cannot retrieve user list from User API")
#     else:
#         data = result.json()

#     return data


def fetch_current_user() -> Any:
    """Fetch current user information."""
    result = authorize(_get)("/my/self")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve current user from User API")
    else:
        data = result.json()

    return data


def fetch_user(user_id: str) -> Any:
    """Fetch information for a specific user."""
    result = authorize(_get)(f"/users/{user_id}")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve user info for user_id '{user_id}' from User API",
        )
    else:
        data = result.json()

    return data


# -------------------------------------------------------------------------- #
# User API (seats)
# -------------------------------------------------------------------------- #


def fetch_current_seats() -> Any:
    """Fetch seats of the current user."""
    result = authorize(_get)("/my/organizations")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve current seat from User API")
    else:
        data = result.json()

    return data


def fetch_current_workspaces() -> list:
    """Fetch workspaces of the current user."""
    result = authorize(_get)("/my/workspaces")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve current workspaces from User API")
    else:
        data = result.json()

    return data


# -------------------------------------------------------------------------- #
# User API (organizations)
# -------------------------------------------------------------------------- #


def fetch_organization(organization_id: str) -> Any:
    """Fetch information for a specific organization."""
    result = authorize(_get)(f"/organizations/{organization_id}")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve organization for organization_id {organization_id} from User API",
        )
    else:
        data = result.json()

    return data


def get_organization_workspaces(organization_id: str) -> list[dict]:
    """Retrieve workspaces from an organization ID."""

    result = authorize(_get)(f"/organization/{organization_id}/workspaces")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve workspaces from organization ID '{organization_id}' from User API",
        )
    else:
        data = result.json()

    return data


def get_plan(plan_id: str) -> dict:
    """Retrieve plan information for a specific plan ID."""

    result = authorize(_get)(f"/plans/{plan_id}")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve plan info for plan ID '{plan_id}' from User API",
        )
    else:
        data = result.json()

    return data


def get_plan_limits(plan_id: str) -> dict:
    """Retrieve plan limits for a specific plan ID."""

    result = authorize(_get)(f"/plans/{plan_id}/limits")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve plan limits for plan ID '{plan_id}' from User API",
        )
    else:
        data = result.json()

    return data


def get_credits_list(organization_id: str) -> dict:
    """Retrieve credits list for a specific organization ID."""

    result = authorize(_get)(
        "/credits",
        params={"organization_id": organization_id},
    )

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve credits list for organization ID '{organization_id}' from User API",
        )
    else:
        data = result.json()

    return data


def get_consumption_history(organization_id: str) -> dict:
    """Retrieve consumption history for a specific organization ID."""

    result = authorize(_get)(
        "/history",
        params={"organization_id": organization_id},
    )

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve consumption history for organization ID '{organization_id}' from User API",
        )
    else:
        data = result.json()

    return data


def get_subject_roles() -> dict[str, list[dict]]:
    """Retrieve subject roles."""

    result = authorize(_get)("/my/roles")

    if result.status_code != "200":
        _handle_error(
            result,
            "Cannot retrieve subject roles from User API",
        )
    else:
        data = result.json()

    return data
