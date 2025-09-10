"""Mixtrain CLI Client

This module provides the HTTP client and core functionality for the Mixtrain SDK.
It handles authentication, API communication, and dataset operations.

"""

import asyncio
import os
from functools import lru_cache
from logging import getLogger
from typing import Any, Dict, Optional

import httpx
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table

from .utils import auth as auth_utils
from .utils.config import get_config

logger = getLogger(__name__)


async def _call_api(
    method: str,
    path: str,
    json: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            config = get_config()
            logger.debug(
                f"Calling {config.platform_url} {method} {path} with json {json}"
            )
            # Only add extra query parameters from params if provided
            query_params = params if params else None
            request_headers = headers.copy() if headers else {}
            auth_token = config.get_auth_token()

            if not auth_token:
                raise Exception("No auth token found")
            request_headers["Authorization"] = f"Bearer {auth_token}"
            if files:
                logger.debug(f"Calling {method} {path} with files {files}")
                response = await client.request(
                    method,
                    f"{config.platform_url}{path}",
                    files=files,
                    params=query_params,
                    headers=request_headers,
                )
            else:
                logger.debug(f"Calling {method} {path} with json {json}")
                response = await client.request(
                    method,
                    f"{config.platform_url}{path}",
                    json=json,
                    params=query_params,
                    headers=request_headers,
                )
            if response.status_code != 200:
                logger.error(
                    f"Error response {response.status_code} while requesting {response.request.url!r}: {response.json()}"
                )
                raise Exception(
                    f"Error: {response.json().get('detail', response.text)}"
                )
            return response
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url!r}.")
            logger.exception(exc)
            raise
        except httpx.HTTPStatusError as exc:
            error_detail = exc.response.json().get("detail", str(exc))
            logger.debug(
                f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {error_detail}"
            )
            logger.exception(exc)
            raise Exception(error_detail)


async def upload_file(dataset_name: str, file_path: str):
    """Upload a file to a dataset"""
    config = get_config()
    workspace_name = config.workspace_name
    with open(file_path, "rb") as f:
        response = await _call_api(
            "POST",
            f"/datasets/{workspace_name}/{dataset_name}/upload",
            files={"file": f},
        )
        return response.json().get("data")


def call_api(
    method: str,
    path: str,
    *,
    json: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    """Synchronous wrapper around async API calls"""
    return asyncio.run(
        _call_api(method, path, json=json, files=files, params=params, headers=headers)
    )


def create_dataset_from_file(
    name: str, file_path: str, description: Optional[str] = None
):
    """Create a dataset from a file using the lakehouse API."""
    config = get_config()
    workspace_name = config.workspace_name

    headers = {}
    if description:
        headers["X-Description"] = description

    with open(file_path, "rb") as f:
        files = {"file": (file_path.split("/")[-1], f, "application/octet-stream")}
        response = call_api(
            "POST",
            f"/lakehouse/workspaces/{workspace_name}/tables/{name}",
            files=files,
            headers=headers,
        )
    return response.json()


def list_datasets():
    """List all datasets in the current workspace"""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api("GET", f"/lakehouse/workspaces/{workspace_name}/tables")
    return response.json()


def delete_dataset(name: str):
    """Delete a dataset"""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api(
        "DELETE", f"/lakehouse/workspaces/{workspace_name}/tables/{name}"
    )
    return response


def set_workspace(workspace_name: str):
    """Set the active workspace"""
    config = get_config()
    config.set_workspace(workspace_name)


def get_workspace() -> str:
    """Get the current workspace name"""
    config = get_config()
    return config.workspace_name


def authenticate_browser() -> str:
    """Authenticate using browser-based OAuth flow."""
    return auth_utils.authenticate_browser(get_config, _call_api)


def authenticate_with_token(token: str, provider: str) -> str:
    """Authenticate using OAuth token (GitHub or Google)."""
    return auth_utils.authenticate_with_token(token, provider, get_config, _call_api)


def authenticate_github(access_token: str) -> str:
    """Authenticate using GitHub access token."""
    return auth_utils.authenticate_github(access_token, get_config, _call_api)


def authenticate_google(id_token: str) -> str:
    """Authenticate using Google ID token."""
    return auth_utils.authenticate_google(id_token, get_config, _call_api)


@lru_cache(maxsize=1)
def get_workspace_name():
    config = get_config()
    return config.workspace_name


@lru_cache(maxsize=1)
def get_catalog(workspace_name: str):
    try:
        provider_secrets = call_api(
            "GET", f"/workspaces/{workspace_name}/dataset-providers/6"
        ).json()
        if provider_secrets["provider_type"] != "apache_iceberg":
            raise Exception(
                f"Dataset provider {provider_secrets['provider_type']} is not supported"
            )

        if (
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None
            and provider_secrets["secrets"]["CATALOG_WAREHOUSE_URI"].startswith("gs://")
            and provider_secrets["secrets"]["SERVICE_ACCOUNT_JSON"]
        ):
            service_account_json = provider_secrets["secrets"]["SERVICE_ACCOUNT_JSON"]
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                f"/tmp/{workspace_name}/service_account.json"
            )

            # Set up Google Cloud credentials (temporary file)
            os.makedirs(f"/tmp/mixtrain/{workspace_name}", exist_ok=True)
            with open(f"/tmp/mixtrain/{workspace_name}/service_account.json", "w") as f:
                f.write(service_account_json)

            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                f"/tmp/{workspace_name}/service_account.json"
            )

        # Load the catalog
        catalog_config = {
            "type": provider_secrets["secrets"]["CATALOG_TYPE"],
            "uri": provider_secrets["secrets"]["CATALOG_URI"],
            "warehouse": provider_secrets["secrets"]["CATALOG_WAREHOUSE_URI"],
        }
        catalog = load_catalog("default", **catalog_config)
        return catalog
    except Exception as e:
        raise Exception(f"Failed to load catalog: {e}")


def get_dataset(name: str) -> Table:
    """Get an Iceberg table using workspace secrets and PyIceberg catalog API.

    This creates a catalog connection using the workspace's dataset provider secrets.
    """

    config = get_config()
    workspace_name = config.workspace_name

    # Extract catalog configuration from secrets
    catalog = get_catalog(workspace_name)
    # Load the table
    table_identifier = f"{workspace_name}.{name}"
    table = catalog.load_table(table_identifier)
    return table


def list_dataset_providers():
    """List available and onboarded dataset providers."""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api("GET", f"/workspaces/{workspace_name}/dataset-providers/")
    return response.json()


def create_dataset_provider(provider_type: str, secrets: Dict[str, str]):
    """Onboard a new dataset provider for the workspace."""
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"provider_type": provider_type, "secrets": secrets}
    response = call_api(
        "POST", f"/workspaces/{workspace_name}/dataset-providers/", json=payload
    )
    return response.json()


def update_dataset_provider(provider_id: int, secrets: Dict[str, str]):
    """Update secrets for an existing dataset provider."""
    config = get_config()
    workspace_name = config.workspace_name
    payload = {"secrets": secrets}
    response = call_api(
        "PUT",
        f"/workspaces/{workspace_name}/dataset-providers/{provider_id}",
        json=payload,
    )
    return response.json()


def delete_dataset_provider(provider_id: int):
    """Remove a dataset provider from the workspace."""
    config = get_config()
    workspace_name = config.workspace_name
    response = call_api(
        "DELETE", f"/workspaces/{workspace_name}/dataset-providers/{provider_id}"
    )
    return response.json()


def get_dataset_metadata(name: str):
    """Get detailed metadata for a table."""
    return get_dataset(name).metadata
