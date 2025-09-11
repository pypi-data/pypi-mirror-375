"""
Methods for using TileDB teamspaces, assets, DAGs, and UDFs.

Examples
--------
Before using any methods, you must log in to TileDB. On your first
login, you must specify a workspace and either a login token or
a username and password. Please note that the names of workspaces,
teamspaces, and assets are only example names.

>>> import tiledb.client
>>> tiledb.client.login(token="TOKEN", workspace="WORKSPACE")

These parameters will be saved to your profiles file. On subsequent
sessions, they can be omitted.

>>> tiledb.client()

The name of the workspace for your current session is accessible from
the client context configuration.

>>> tiledb.client.Ctx().config()["rest.workspace"]
"WORKSPACE"

The list of teamspaces you can access is provided by the `teamspaces`
module.

>>> from tiledb.client import teamspaces
>>> [item.name for item in teamspaces.list_teamspaces()]
["general"]

The list of assets in in a teamspace is provided by the `assets` module.

>>> from tiledb.client import assets
>>> [item.name for item in assets.list_assets(teamspace="general")]
["README.md"]

"""

from . import array
from . import assets
from . import compute
from . import dag
from . import files
from . import folders
from . import groups
from . import sql
from . import teamspaces
from . import tokens
from . import udf
from . import workspaces
from ._common import pickle_compat as _pickle_compat
from .client import Config
from .client import Ctx
from .client import login

_pickle_compat.patch_cloudpickle()
_pickle_compat.patch_pandas()

try:
    from tiledb.client.version import version as __version__
except ImportError:
    __version__ = "0.0.0.local"

__all__ = (
    "Config",
    "Ctx",
    "array",
    "asset",
    "assets",
    "compute",
    "dag",
    "files",
    "folders",
    "groups",
    "login",
    "sql",
    "teamspaces",
    "tokens",
    "udf",
    "workspaces",
)
