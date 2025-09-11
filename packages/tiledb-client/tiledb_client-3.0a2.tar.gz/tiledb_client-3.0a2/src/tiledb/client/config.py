from typing import Optional

from urllib3 import Retry

import tiledb
from tiledb.client._common.api_v4 import configuration
from tiledb.client._common.api_v4 import models

default_host = "http://localhost:8181"


class ConfigurationError(tiledb.TileDBError):
    """Raise for configuration-related errors"""


# Starting with version 0.12.30, "config" is a dynamic attribute of
# this module. The actual state of the attribute is bound to "_config",
# which begins uninitialized. Looking up "config" from
# tiledb.client.config causes our stored configuration to be loaded
# just as needed.
_config = configuration.Configuration()


def __getattr__(name):
    global logged_in
    if name == "config":
        if not logged_in:
            logged_in = load_configuration()
        return _config
    else:
        raise AttributeError


def parse_bool(s: str) -> bool:
    return s.lower() in ["true", "1", "on"]


def save_configuration(
    profile_name: Optional[str] = None, profile_dir: Optional[str] = None
):
    """Saves the current configuration into a TileDB profile."""
    profile = tiledb.Profile(profile_name, profile_dir)
    if (
        _config.api_key is not None
        and _config.api_key != ""
        and "X-TILEDB-REST-API-KEY" in _config.api_key
    ):
        profile["rest.token"] = _config.api_key["X-TILEDB-REST-API-KEY"]
    if _config.username is not None and _config.username != "":
        profile["rest.username"] = _config.username
    if _config.password is not None and _config.password != "":
        profile["rest.password"] = _config.password
    if _config.host is not None and _config.host != "":
        profile["rest.server_address"] = _config.host
    if _config.verify_ssl is not None and _config.verify_ssl is False:
        # Store verify_ssl only when it is False.
        profile["rest.verify_ssl"] = str(_config.verify_ssl).lower()
    if _workspace_id is not None:
        profile["rest.workspace"] = _workspace_id

    try:
        # Remove any existing profile.
        tiledb.Profile.remove(profile_name, profile_dir)
    except Exception:
        # If the profile does not exist, we can ignore this error.
        pass

    profile.save()


def load_configuration():
    """Loads the configuration from a saved profile."""

    logged_in = True

    config_py = tiledb.Config()
    # This config will be using the default TileDB profile if found.

    token = config_py.get("rest.token", False)
    username = config_py.get("rest.username", False)
    password = config_py.get("rest.password", False)
    host = config_py.get("rest.server_address", False)
    verify_ssl = config_py.get("rest.verify_ssl", False)
    workspace = config_py.get("rest.workspace", False)

    if (token is None or token == "") and (username is None or username == ""):
        raise ConfigurationError(
            "You must first login before you can run commands."
            " Please run tiledb.client.login."
        )

    if token is not None and token != "":
        token = {"X-TILEDB-REST-API-KEY": token}
    else:
        token = {}

    if host is None or host == "":
        global default_host
        host = default_host

    setup_configuration(
        api_key=token,
        username=username,
        password=password,
        host=host,
        verify_ssl=verify_ssl,
        workspace=workspace,
    )
    return logged_in


def setup_configuration(
    api_key=None,
    host="",
    username=None,
    password=None,
    verify_ssl=True,
    workspace=None,
):
    if api_key is None:
        api_key = {}
    _config.api_key = api_key
    _config.host = host
    _config.username = username
    _config.password = password
    _config.verify_ssl = verify_ssl
    _config.retries = Retry(
        total=10,
        backoff_factor=0.25,
        status_forcelist=[503],
        allowed_methods=[
            "HEAD",
            "GET",
            "PUT",
            "DELETE",
            "OPTIONS",
            "TRACE",
            "POST",
            "PATCH",
        ],
        raise_on_status=False,
        # Don't remove any headers on redirect
        remove_headers_on_redirect=[],
    )
    # Set logged in at this point
    global logged_in
    logged_in = True
    global _workspace_id
    _workspace_id = workspace


# Loading of the default configuration file and determination of
# whether we are logged in or not is now deferred to the first access
# of this module's "config" attribute.
_workspace_id = None
logged_in = None
"""Whether logged in or not, and into which workspace."""


user: Optional[models.User] = None
"""The default user to use.

You should probably access this through ``client.default_user()`` rather than
doing so directly.
"""
