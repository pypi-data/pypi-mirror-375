import enum
import logging
import os
import threading
import types
import uuid
import warnings
from concurrent import futures
from typing import Callable, Optional, Sequence, TypeVar, Union

import urllib3

import tiledb
import tiledb.client._common.api_v2.models as models_v2
import tiledb.client._common.api_v4.models as models_v4
import tiledb.client.rest_api.models as models_v1
from tiledb.client import config
from tiledb.client import rest_api
from tiledb.client._common.api_v4 import ApiClient
from tiledb.client._common.api_v4 import APIToken
from tiledb.client._common.api_v4 import TokenCreateRequest
from tiledb.client._common.api_v4 import TokensApi
from tiledb.client._common.api_v4 import TokenScope
from tiledb.client._common.api_v4 import User
from tiledb.client._common.api_v4 import UsersApi
from tiledb.client._common.api_v4 import UserSelfWorkspace
from tiledb.client._common.api_v4 import WorkspacesApi
from tiledb.client.pool_manager_wrapper import _PoolManagerWrapper

_T = TypeVar("_T")

logger = logging.getLogger(__name__)


def Config(cfg_dict=None):
    """
    Builds a tiledb config setting the login parameters that exist for the cloud service
    :return: tiledb.Config
    """
    restricted = ("rest.server_address", "rest.username", "rest.password")

    if not cfg_dict:
        cfg_dict = dict()

    for r in restricted:
        if r in cfg_dict:
            raise ValueError(f"Unexpected config parameter '{r}' to cloud.Config")

    host = config.config.host

    cfg_dict["rest.server_address"] = host
    cfg = tiledb.Config(cfg_dict)

    if (
        config.config.username is not None
        and config.config.username != ""
        and config.config.password is not None
        and config.config.password != ""
    ):
        cfg["rest.username"] = config.config.username
        cfg["rest.password"] = config.config.password
    else:
        cfg["rest.token"] = config.config.api_key["X-TILEDB-REST-API-KEY"]

    return cfg


def Ctx(config=None):
    """
    Builds a TileDB Context that has the tiledb config parameters
    for tiledb cloud set from stored login
    :return: tiledb.Ctx
    """
    return tiledb.Ctx(Config(config))


class LoginError(tiledb.TileDBError):
    """Raise for errors during login"""


def login(
    token: Optional[Union[APIToken, str]] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    workspace: Optional[str] = None,
    host: Optional[str] = None,
    verify_ssl: Optional[bool] = None,
    no_session: Optional[bool] = False,
    threads: Optional[int] = None,
    profile_name: Optional[str] = None,
    profile_dir: Optional[str] = None,
) -> None:
    """
    Login and initialize a session

    One of a token or username/password pair are required to login. The
    name or id of a workspace is also required unless it is borne by the
    provided ApiToken object.

    :param token: API token for login
    :type token: ApiToken or str, optional
    :param username: username for login
    :type username: str, optional
    :param password: password for login
    :type password: str, optional
    :param workspace: TileDB workspace name
    :type workspace: str, optional
    :param host: host to login to. the tiledb.client.regions module
        contains region-specific host constants.
    :type host: str, optional
    :param verify_ssl: Enable strict SSL verification, defaults to
        False
    :type verify_ssl: bool, optional
    :param no_session: don't create a session token on login, store
        instead username/password, defaults to False
    :type no_session: bool, optional
    :param threads: number of threads to enable for concurrent
        requests, default to None (determined by library)
    :type threads: int, optional
    :param profile_name: name of the profile to use in order to fetch credentials
    :type profile_name: str, optional
    :param profile_dir: directory where the profiles file is stored.
        Defaults to None, which means the home directory of the user.
    :type profile_dir: str, optional
    :raises LoginError: if the login fails due to missing parameters
    """

    # Attempt to load the profile if it exists.
    # If no profile details are provided, we will use the default.
    try:
        profile = tiledb.Profile.load(profile_name, profile_dir)
    except tiledb.TileDBError:
        if (
            (profile_name or profile_dir)
            and (token is None or token == "")
            and (username is None or username == "")
            and (password is None or password == "")
        ):
            raise LoginError(
                f"Could not load profile"
                f"{f' {profile_name}' if profile_name else ''}"
                f"{f' from {profile_dir}' if profile_dir else ''}"
            )
        profile = None

    if profile:
        # Update the parameters with values from the profile if they are not set.
        def get_val(key, current):
            if current is not None:
                return current
            try:
                return profile.get(key, False)
            except Exception:
                return None

        username = get_val("rest.username", username)
        password = get_val("rest.password", password)
        workspace = get_val("rest.workspace", workspace)
        token = get_val("rest.token", token)
        host = get_val("rest.server_address", host)

    if host is None:
        host = config.default_host

    # See sc-56351. Usually, a hostname doesn't include a protocol
    # scheme, but our SDK strictly requires the http(s) scheme.
    elif not host.startswith(("http://", "https://")):
        host = f"https://{host}"

    # Strip trailing slashes from the host.
    host = host.rstrip("/")

    if (token is None or token == "") and (
        (username is None or username == "") and (password is None or password == "")
    ):
        raise LoginError("Username and Password OR token must be set.")
    if (username is None or username == "" or password is None or password == "") and (
        token is None or token == ""
    ):
        raise LoginError("Username and Password are both required.")
    # if token and workspace:
    #     raise LoginError("Workspace cannot be used with a token.")

    if verify_ssl is None:
        verify_ssl = not config.parse_bool(
            os.getenv("TILEDB_REST_IGNORE_SSL_VALIDATION", "False")
        )

    config_args = {
        "username": username,
        "password": password,
        "host": host,
        "verify_ssl": verify_ssl,
        "api_key": {},
    }

    # If user logs in with username/password we need to create a session
    if (token is None or token == "") and not no_session:
        if not workspace:
            raise LoginError(
                "Workspace is required when logging in with username and password."
            )

        config.setup_configuration(**config_args)
        client.set_threads(threads)

        # Create a session type token with maximum scope.
        with ApiClient(config.config) as api_client:
            # Get workspace id from name.
            workspaces_api = WorkspacesApi(api_client)
            resp = workspaces_api.get_workspace(workspace)
            workspace = resp.data.workspace_id

            request = TokenCreateRequest(
                name=f"login-session-{uuid.uuid4()}",
                scope=TokenScope._,
            )
            tokens_api = TokensApi(api_client)

            logger.debug(
                "Creating token: request=%r, host=%r, workspace_id=%r",
                request,
                config.config.host,
                workspace,
            )

            resp = tokens_api.create_token(request)
            token = resp.data

            logger.debug("Created token: resp=%r, token=%r", resp, token)

    if token is not None and token != "":
        workspace = workspace or getattr(token, "workspace_id", None)
        if not workspace:
            raise LoginError("Unknown workspace.")

        api_key = getattr(token, "api_key", token)
        config_args["api_key"] = {"X-TILEDB-REST-API-KEY": api_key}
        del config_args["username"]
        del config_args["password"]

    config.setup_configuration(**config_args)
    config._workspace_id = workspace

    try:
        config.save_configuration(profile_name, profile_dir)
    except IOError:
        warnings.warn(
            UserWarning(
                "Could not save TileDB Profile; login will expire"
                " when this program exits."
            )
        )

    config.logged_in = True


def get_workspace_id() -> str:
    """Get the current session's workspace id."""
    return config._workspace_id


def get_self_user() -> tuple[User, UserSelfWorkspace]:
    """Get the currently logged-in user and related workspaces.

    Returns
    -------
    tuple[User, UserSelfWorkspace]
    """
    api_instance = build(UsersApi)
    get_self_user_response = api_instance.get_self_user()
    return (get_self_user_response.data.user, get_self_user_response.data.workspaces)


def default_user() -> User:
    """Get the currently logged-in user..

    Returns
    -------
    User
    """
    user, _ = get_self_user()
    return user


class RetryMode(enum.Enum):
    DEFAULT = "default"
    FORCEFUL = "forceful"
    DISABLED = "disabled"

    def maybe_from(v: "RetryOrStr") -> "RetryMode":
        if isinstance(v, RetryMode):
            return v
        return RetryMode(v)


RetryOrStr = Union[RetryMode, str]


_RETRY_CONFIGS = {
    RetryMode.DEFAULT: urllib3.Retry(
        total=100,
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
    ),
    RetryMode.FORCEFUL: urllib3.Retry(
        total=100,
        backoff_factor=0.25,
        status_forcelist=[400, 500, 501, 502, 503],
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
    ),
    RetryMode.DISABLED: False,
}


class Client:
    """
    TileDB Client.

    :param pool_threads: Number of threads to use for http requests
    :param retry_mode: Retry mode ["default", "forceful", "disabled"]
    """

    def __init__(
        self,
        pool_threads: Optional[int] = None,
        retry_mode: RetryOrStr = RetryMode.DEFAULT,
    ):
        """

        :param pool_threads: Number of threads to use for http requests
        :param retry_mode: Retry mode ["default", "forceful", "disabled"]
        """
        self._pool_lock = threading.Lock()
        self._set_threads(pool_threads)
        # Low-level clients begin uninitialized.
        # They are initialized just before they are needed.
        self._mode = retry_mode
        self.__client_v1 = None
        self.__client_v2 = None
        self.__client_v4 = None

    @property
    def _client_v1(self):
        if not self.__client_v1:
            self._retry_mode(self._mode)
            self._rebuild_clients()
        return self.__client_v1

    @property
    def _client_v2(self):
        if not self.__client_v2:
            self._retry_mode(self._mode)
            self._rebuild_clients()
        return self.__client_v2

    @property
    def _client_v4(self):
        if not self.__client_v4:
            self._retry_mode(self._mode)
            self._rebuild_clients()
        return self.__client_v4

    def build(self, builder: Callable[[rest_api.ApiClient], _T]) -> _T:
        """Builds an API client with the given config."""
        if builder.__module__.startswith("tiledb.client._common.api_v4"):
            return builder(self._client_v4)
        elif builder.__module__.startswith("tiledb.client._common.api_v2"):
            return builder(self._client_v2)
        return builder(self._client_v1)

    def set_disable_retries(self):
        self.retry_mode(RetryMode.DISABLED)

    def set_default_retries(self):
        self.retry_mode(RetryMode.DEFAULT)

    def set_forceful_retries(self):
        self.retry_mode(RetryMode.FORCEFUL)

    def retry_mode(self, mode: RetryOrStr = RetryMode.DEFAULT) -> None:
        """Sets how we should retry requests and updates API instances."""
        self._retry_mode(mode)
        self._rebuild_clients()

    def set_threads(self, threads: Optional[int] = None) -> None:
        """Updates the number of threads in the async thread pool."""
        self._set_threads(threads)
        self._rebuild_clients()

    def _retry_mode(self, mode: RetryOrStr) -> None:
        mode = RetryMode.maybe_from(mode)
        config.config.retries = _RETRY_CONFIGS[mode]
        self._mode = mode

    def _rebuild_clients(self) -> None:
        self.__client_v1 = self._rebuild_client(models_v1)
        self.__client_v2 = self._rebuild_client(models_v2)
        self.__client_v4 = self._rebuild_client(models_v4)

    def _rebuild_client(self, module: types.ModuleType) -> rest_api.ApiClient:
        """
        Initialize api clients
        """
        # If users increase the size of the thread pool, increase the size
        # of the connection pool to match. (The internal members of
        # ThreadPoolExecutor are not exposed in the .pyi files, so we silence
        # mypy's warning here.)
        pool_size = self._thread_pool._max_workers  # type: ignore[attr-defined]
        config.config.connection_pool_maxsize = pool_size
        client = rest_api.ApiClient(config.config, _tdb_models_module=module)
        client.rest_client.pool_manager = _PoolManagerWrapper(
            client.rest_client.pool_manager
        )
        return client

    def _set_threads(self, threads) -> None:
        with self._pool_lock:
            old_pool = getattr(self, "_thread_pool", None)
            self._thread_pool = futures.ThreadPoolExecutor(
                threads, thread_name_prefix="tiledb-async-"
            )
        if old_pool:
            old_pool.shutdown(wait=False)

    def _pool_submit(
        self,
        func: Callable[..., _T],
        *args,
        **kwargs,
    ) -> "futures.Future[_T]":
        with self._pool_lock:
            return self._thread_pool.submit(func, *args, **kwargs)


client = Client()

build = client.build


def _maybe_unwrap(param: Union[None, str, Sequence[str]]) -> Optional[str]:
    """Unwraps the first value if passed a sequence of strings."""
    if param is None or isinstance(param, str):
        return param
    try:
        return param[0]
    except IndexError:
        # If we're passed an empty sequence, treat it as no parameter.
        return None


def _uuid_to_str(param: Union[None, str, uuid.UUID]) -> Optional[str]:
    if isinstance(param, uuid.UUID):
        return str(param)
    return param


def _maybe_wrap(param: Union[None, str, Sequence[str]]) -> Optional[Sequence[str]]:
    """Wraps the value in a sequence if passed an individual string."""
    if isinstance(param, str):
        return (param,)
    return param
