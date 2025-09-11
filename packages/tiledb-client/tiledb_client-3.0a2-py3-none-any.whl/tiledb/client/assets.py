"""An Asset is an item in the TileDB Catalog.

An Asset may represent an Array, a Group of Arrays, a Folder, or a File.

When a Folder is created, it becomes an asset and a corresponded Asset
is created in the Catalog. When a file is uploaded, it becomes an asset.
Similarly, creation or registration of arrays and groups produces new
assets in the Catalog.



"""

import pathlib
from typing import Any, Mapping, Optional, Sequence, Union

import numpy

import tiledb
from tiledb.datatypes import DataType

from . import client
from ._common.api_v4 import Asset
from ._common.api_v4 import AssetMemberType  # noqa: F401
from ._common.api_v4 import AssetMetadataSaveRequestInner
from ._common.api_v4 import AssetMetadataType
from ._common.api_v4 import AssetRegisterRequest
from ._common.api_v4 import AssetsApi
from ._common.api_v4 import AssetType
from ._common.api_v4 import Teamspace
from .pager import Pager
from .rest_api import ApiException


class AssetsError(tiledb.TileDBError):
    """Raised when assets can not be accessed."""


def list_assets(
    # Search is not implemented on server yet.
    search: Optional[str] = None,
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
    path: Optional[str] = "",
    type: Optional[str] = None,
    created_by: Optional[str] = None,
    expand: Optional[str] = None,
    page: Optional[int] = 1,
    per_page: Optional[int] = None,
    order_by: Optional[str] = None,
) -> Pager[Asset]:
    """List/search the Catalog for assets.

    An asset listing consists of a sequence of "pages", or
    batches, of lists of assets. This function returns a Pager object
    that represents one page of the listing. The object also serves as
    an iterator over all assets from that page to the last page, and it
    can be indexed to get all or a subset of assets from that page to
    the last page.

    Without parameters, this function will query all accessible assets,
    public or in private teamspaces that the user is a member of.

    Parameters
    ----------
    search : str
        Search keywords.
    teamspace : Teamspace or str, optional
        The teamspace to search within, specified by object or id.
    path : str, optional
        The path to search within. To list all assets in a teamspace,
        pass the empty string.
    type : str, optional
        Filters for assets of the specified type. Allowed types are
        enumerated by the AssetType class.
    created_by : str, optional
        Filters for assets created by a named user.
    expand : str, optional
        Specifies profiles of additional information
        to include in the response.
    page : int, optional
        Which page of results to retrieve. 1-based.
    per_page : int, optional
        How many results to include on each page.
    order_by : str, optional.
        The order to return assets, by default "created_at desc".
        Supported keys are "created_at", "name", and "asset_type".  They
        can be used alone or with "asc" or "desc" separated by a space
        (e.g. "created_at", "asset_type asc").

    Returns
    -------
    Pager for Assets

    Raises
    ------
    AssetsError
        Raised when assets can not be accessed.

    """

    if type is not None and type not in AssetType.allowable_values:
        raise AssetsError("Not a known asset type.")

    try:
        resp = Pager(
            client.client.build(AssetsApi).list_assets,
            client.get_workspace_id(),
            getattr(teamspace, "teamspace_id", teamspace),
            path,
            asset_type=type,
            created_by=created_by,
            per_page=per_page,
            expand=expand,
            order_by=order_by,
        )
        resp.call_page(page)
    except ApiException as exc:
        raise AssetsError("The asset listing request failed.") from exc
    else:
        return resp


def get_asset(
    asset: Union[object, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> Asset:
    """Retrieve the representation of an asset by object, path, or id.

    The catalog representation of a Folder, File, Array, or Group may be
    identified by its object representation, path relative to
    a teamspace, or asset id.

    Parameters
    ----------
    asset : Asset or str
        The target asset, specified by object, path, or id.
    teamspace : Teamspace or str, optional
        The teamspace to search within, specified by object or id. If
        not provided, the `asset` parameter is queried for a teamspace
        id.

    Returns
    -------
    Asset

    Raises
    ------
    AssetsError
        Raised when an asset representation cannot be retrieved.

    Examples
    --------
    >>> obj = get_asset(
    ...     "path/to/asset",
    ...     teamspace="teamspace_id",
    ... )

    """

    teamspace_id = (
        teamspace and getattr(teamspace, "teamspace_id", teamspace)
    ) or getattr(asset, "teamspace_id")
    asset_id = getattr(asset, "asset_id", asset)

    try:
        resp = client.client.build(AssetsApi).get_asset(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
        )
    except ApiException as exc:
        raise AssetsError("The asset metadata creation request failed.") from exc
    else:
        return resp.data


def delete_metadata(
    asset: Union[object, str],
    keys: Sequence[str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> None:
    """Delete asset metadata.

    Metadata are represented as a Python dict with string keys and
    values that can be any builtin Python type or Numpy scalar.

    Parameters
    ----------
    asset : obj or str
        The target asset, specified by object or id.
    keys : Sequence
        A sequence of keys to delete along with their values.
    teamspace : Teamspace or str, optional
        The teamspace to search within, specified by object or id. If
        not provided, the `asset` parameter is queried for a teamspace
        id.

    Returns
    -------
    None

    Raises
    ------
    AssetsError
        Raised when metadata can not be created and saved.

    Examples
    --------
    >>> delete_metadata(
    ...     "asset_id",
    ...     ["field1"],
    ...     teamspace="teamspace_id",
    ... )

    """

    teamspace_id = (
        teamspace and getattr(teamspace, "teamspace_id", teamspace)
    ) or getattr(asset, "teamspace_id")
    asset_id = getattr(asset, "asset_id", asset)

    try:
        client.client.build(AssetsApi).delete_asset_metadata(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
            list(keys),
        )
    except ApiException as exc:
        raise AssetsError("The asset metadata deletion request failed.") from exc


def update_metadata(
    asset: Union[object, str],
    items: Mapping[str, Any],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> None:
    """Update asset metadata.

    Metadata are represented as a Python dict with string keys and
    values that can be any builtin Python type or Numpy scalar.

    Parameters
    ----------
    asset : obj or str
        The target asset, specified by object or id.
    items : Mapping
        A mapping of metadata keys and values.
    teamspace : Teamspace or str, optional
        The teamspace to search within, specified by object or id. If
        not provided, the `asset` parameter is queried for a teamspace
        id.

    Returns
    -------
    None

    Raises
    ------
    AssetsError
        Raised when metadata can not be created and saved.

    Examples
    --------
    >>> update_metadata(
    ...     "asset_id",
    ...     {"field1": "another string", "field2": numpy.float64(4.2)},
    ...     teamspace="teamspace_id",
    ... )

    """

    teamspace_id = (
        teamspace and getattr(teamspace, "teamspace_id", teamspace)
    ) or getattr(asset, "teamspace_id")
    asset_id = getattr(asset, "asset_id", asset)
    metadata = [
        AssetMetadataSaveRequestInner(
            key=k,
            value=str(v),
            type=getattr(
                AssetMetadataType,
                DataType.from_numpy(numpy.array(v).dtype).tiledb_type.name,
            ),
        )
        for k, v in items.items()
    ]

    try:
        _ = client.client.build(AssetsApi).update_asset_metadata(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
            metadata,
        )
    except ApiException as exc:
        raise AssetsError("The asset metadata creation request failed.") from exc


def get_metadata(
    asset: Union[object, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> dict:
    """Retrieve asset metadata.

    Metadata are represented as a Python dict with string keys and
    values that can be any builtin Python type or Numpy scalar.

    Parameters
    ----------
    asset : obj or str
        The target asset, specified by object or id.
    teamspace : Teamspace or str, optional
        The teamspace to search within, specified by object or id. If
        not provided, the `asset` parameter is queried for a teamspace
        id.

    Returns
    -------
    dict

    Raises
    ------
    AssetsError
        Raised when metadata can not be created and saved.

    Examples
    --------
    >>> get_metadata("asset_id", teamspace="teamspace_id")

    """

    teamspace_id = (
        teamspace and getattr(teamspace, "teamspace_id", teamspace)
    ) or getattr(asset, "teamspace_id")
    asset_id = getattr(asset, "asset_id", asset)

    try:
        resp = client.client.build(AssetsApi).get_asset_metadata(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
        )
    except ApiException as exc:
        raise AssetsError("The asset metadata retrieval request failed.") from exc
    else:
        items = [
            (
                md.key,
                tiledb.datatypes.DataType.from_tiledb(
                    getattr(tiledb.datatypes.lt.DataType, md.type.upper())
                ).np_dtype.type(md.value),
            )
            for md in resp.data
        ]
        return dict(items)


def register_asset(
    teamspace: Union[Teamspace, str],
    uri: str,
    path: str,
    acn: Optional[str] = None,
) -> None:
    """Register an object in cloud storage with the catalog.

    Parameters
    ----------
    teamspace : Teamspace or str
        The teamspace to which the object will be registered.
    uri : str
        Object identifier. For example: "s3://bucket/prefix/file".
    path : str
        The TileDB path at which the object will be registered.
    acn : str, optional
        The name of a stored credential for accessing the object.

    Returns
    -------
    None

    Raises
    ------
    AssetsError:
        If the registration failed.

    Examples
    --------
    >>> assets.register_asset(
    ...     "teamspace",
    ...     "s3://bucket/prefix/file",
    ...     "/file",
    ...     acn="bucket-credentials",
    ... )

    """
    teamspace_id = getattr(teamspace, "teamspace_id", teamspace)
    name = pathlib.Path(path).stem
    req = AssetRegisterRequest(
        name=name, uri=uri, access_credentials_name=acn, path=path
    )
    try:
        client.client.build(AssetsApi).register_asset(
            client.get_workspace_id(), teamspace_id, req
        )
    except ApiException as exc:
        raise AssetsError("The asset registration request failed.") from exc
