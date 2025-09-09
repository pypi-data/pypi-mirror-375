import os
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal

from sema4ai.actions import ActionError

_SPCS_TOKEN_FILE_PATH = Path("/snowflake/session/token")
_LOCAL_AUTH_FILE_PATH = Path.home() / ".sema4ai" / "sf-auth.json"


@dataclass(init=False)
class LinkingDetails:
    account: str
    user: str
    role: str
    authenticator: Literal["ID_TOKEN", "OAUTH", "SNOWFLAKE_JWT"]
    applicationUrl: str
    privateKeyPath: str
    privateKeyPassphrase: str | None = None

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)


@dataclass
class SnowflakeAuth:
    linkingDetails: LinkingDetails

    @classmethod
    def from_dict(cls, data: dict) -> "SnowflakeAuth":
        return cls(
            linkingDetails=LinkingDetails(**data["linkingDetails"]),
        )


class SnowflakeAuthenticationError(ActionError):
    """Raised when there are authentication-related issues with Snowflake connection."""

    pass


def get_snowflake_connection_details(
    role: str | None = None,
    warehouse: str | None = None,
    database: str | None = None,
    schema: str | None = None,
) -> dict:
    """
    Get Snowflake connection details based on the environment.

    This function first checks if running in SPCS by looking for the token file.
    If found, it uses SPCS authentication, otherwise falls back to local config-based authentication.

    Args:
        role: Snowflake role to use. Falls back to env var
        warehouse: Snowflake warehouse to use. Falls back to env var
        database: Snowflake database to use. Falls back to env var
        schema: Snowflake schema to use. Falls back to env var

    Returns:
        dict: Connection credentials for Snowflake containing environment-specific fields:
            For SPCS:
               host: from SNOWFLAKE_HOST env var
               account: from SNOWFLAKE_ACCOUNT env var
               authenticator: "OAUTH"
               token: from SPCS token file
               role, warehouse, database, schema: from args or env vars
               client_session_keep_alive: True
               port: from SNOWFLAKE_PORT env var
               protocol: "https"
            For local machine:
               account: from config
               user: from config
               role: from args or config
               authenticator: from config (ID_TOKEN, OAUTH, or SNOWFLAKE_JWT)
               warehouse, database, schema: from args
               client_session_keep_alive: True
            Plus authentication-specific fields:
               For ID_TOKEN: session_token and auth_class
               For OAUTH: token
               For SNOWFLAKE_JWT: private_key and private_key_password

    Raises:
        SnowflakeAuthenticationError: If required credentials are missing or invalid
    """
    # Check for SPCS environment first
    import json

    if _SPCS_TOKEN_FILE_PATH.exists():
        token = _SPCS_TOKEN_FILE_PATH.read_text().strip()

        host = os.getenv("SNOWFLAKE_HOST")
        account = os.getenv("SNOWFLAKE_ACCOUNT")

        if not host or not account:
            raise SnowflakeAuthenticationError(
                "Required environment variables SNOWFLAKE_HOST and SNOWFLAKE_ACCOUNT must be set"
            )

        return {
            "host": host,
            "account": account,
            "authenticator": "OAUTH",
            "token": token,
            "role": role or os.getenv("SNOWFLAKE_ROLE"),
            "warehouse": warehouse or os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": database or os.getenv("SNOWFLAKE_DATABASE"),
            "schema": schema or os.getenv("SNOWFLAKE_SCHEMA"),
            "client_session_keep_alive": True,
            "port": os.getenv("SNOWFLAKE_PORT"),
            "protocol": "https",
        }

    # Fall back to local config-based authentication
    if not _LOCAL_AUTH_FILE_PATH.exists():
        raise SnowflakeAuthenticationError(
            "Not linked to Snowflake, missing authentication data."
        )

    try:
        auth_data = json.loads(_LOCAL_AUTH_FILE_PATH.read_text())
        sf_auth = SnowflakeAuth.from_dict(auth_data)
    except Exception as e:
        raise SnowflakeAuthenticationError(
            f"Failed to read authentication config: {str(e)}"
        )

    config = {
        "account": sf_auth.linkingDetails.account,
        "user": sf_auth.linkingDetails.user,
        "role": role or sf_auth.linkingDetails.role,
        "authenticator": sf_auth.linkingDetails.authenticator,
        "warehouse": warehouse,
        "database": database,
        "schema": schema,
        "client_session_keep_alive": True,
    }

    if sf_auth.linkingDetails.authenticator == "SNOWFLAKE_JWT":
        config["private_key_file"] = sf_auth.linkingDetails.privateKeyPath
        if sf_auth.linkingDetails.privateKeyPassphrase:
            config["private_key_file_pwd"] = sf_auth.linkingDetails.privateKeyPassphrase

    else:
        raise SnowflakeAuthenticationError(
            f"Unsupported authenticator: {sf_auth.linkingDetails.authenticator}"
        )

    return config
