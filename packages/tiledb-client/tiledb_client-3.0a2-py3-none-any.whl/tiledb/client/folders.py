"""TileDB folders.

This module contains functions that operate on a teamspace; adding,
removing, retrieving, or listing folders. It also contains functions
operating on a folder; adding, removing, or listing asset contents; or
updating folder properties.

Model classes associated with these functions are also exported from
this module.
"""

import logging
import pathlib
from typing import Optional, Union

import tiledb
from tiledb.client import client
from tiledb.client._common.api_v4 import Asset
from tiledb.client._common.api_v4 import Folder
from tiledb.client._common.api_v4 import FolderCreateRequestInner
from tiledb.client._common.api_v4 import FoldersApi
from tiledb.client._common.api_v4 import FoldersContentsModifyInner
from tiledb.client._common.api_v4 import FolderUpdateRequest
from tiledb.client._common.api_v4 import Teamspace

from .rest_api import ApiException

logger = logging.getLogger(__name__)


class FoldersError(tiledb.TileDBError):
    """Raised when a folder CRUD operation fails."""


def create_folder(
    teamspace: Union[Teamspace, str],
    path: str,
    *,
    description: Optional[str] = None,
    parents: Optional[bool] = False,
    exist_ok: Optional[bool] = False,
) -> Folder:
    """Create a new folder in a teamspace.

    Optionally, parents of the new folder can also be created.

    Parameters
    ----------
    teamspace : Teamspace or str
        The teamspace for the folder.
    name_or_path : str
        The name or path of the folder to create.
    description : str, optional
        Description of the folder to create.
    parents : bool, optional
        If True, parents will be created as needed. If False,
        a FoldersError will be raised if a parent is missing.
    exist_ok : bool, optional
        If False, a FoldersError will be raised if the folder already
        exists.

    Returns
    -------
    Folder

    Raises
    ------
    FoldersError:
        If the folder creation request failed.

    Examples
    --------
    >>> folder1 = folders.create_folder(
    ...     "teamspace",
    ...     "folder1",
    ...     description="Folder One",
    ... )
    >>> folder2 = folders.create_folder(
    ...     "teamspace",
    ...     "folder1/folder2",
    ...     description="Folder Two",
    ... )

    """
    tdb_path = pathlib.Path(path.strip("/"))

    # Traverse the destination path's parents, in reverse order.
    # We materialize the parents iterator to work around
    # https://github.com/python/cpython/issues/79679 for Python 3.9.
    for path in list(tdb_path.parents)[-2::-1]:
        try:
            _ = client.client.build(FoldersApi).get_folder(
                client.get_workspace_id(),
                getattr(teamspace, "teamspace_id", teamspace),
                path.as_posix(),
            )
        except ApiException:
            if not parents:
                raise FoldersError("A parent folder does not exist.")
            else:
                try:
                    logger.debug(f"Creating parent folder: {path=}")
                    _ = client.client.build(FoldersApi).create_folder(
                        client.get_workspace_id(),
                        getattr(teamspace, "teamspace_id", teamspace),
                        path.as_posix(),
                        FolderCreateRequestInner(description=""),
                    )
                except ApiException as exc:
                    raise FoldersError("The folder creation request failed.") from exc
    else:
        try:
            resp = client.client.build(FoldersApi).get_folder(
                client.get_workspace_id(),
                getattr(teamspace, "teamspace_id", teamspace),
                tdb_path.as_posix(),
            )
        except ApiException:
            try:
                resp = client.client.build(FoldersApi).create_folder(
                    client.get_workspace_id(),
                    getattr(teamspace, "teamspace_id", teamspace),
                    tdb_path.as_posix(),
                    FolderCreateRequestInner(description=(description or "")),
                )
            except ApiException as exc:
                raise FoldersError("The folder creation request failed.") from exc
        else:
            if not exist_ok:
                raise FoldersError("A folder exists at the specified path.")

    return resp.data


def _find_ids(
    teamspace: Union[Teamspace, str, None], folder: Union[Asset, Folder, str]
) -> tuple[str, str]:
    try:
        teamspace_id = getattr(teamspace, "teamspace_id", teamspace) or getattr(
            folder, "teamspace_id"
        )
        asset_id = getattr(folder, "asset_id", None) or getattr(folder, "id", folder)
        if not isinstance(teamspace_id, str):
            raise TypeError("teamspace_id was not a string.")
        if not isinstance(asset_id, str):
            raise TypeError("asset_id was not a string.")
    except (AttributeError, TypeError) as exc:
        raise FoldersError("A folder was not specified.") from exc
    else:
        return teamspace_id, asset_id


def get_folder(
    folder: Union[Folder, Asset, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> Folder:
    """Retrieve the representation of a TileDB folder.

    The folder may be identified by asset id, path relative to
    a teamspace, or object representation (Folder or Asset instance).

    Parameters
    ----------
    folder : Asset, Folder, or str
        The object representation, name, or path of an existing folder.
    teamspace : Teamspace or str, optional
        The representation or string identifier of the folder's
        teamspace. If the folder parameter is a Folder instance, the
        teamspace will be obtained from it.

    Returns
    -------
    Folder

    Raises
    ------
    FolderError
        If the folder cannot be retrieved.

    Examples
    --------
    >>> folder1 = get_folder("folder1", teamspace="teamspace")
    >>> folder2 = get_folder("folder1/folder2", teamspace="teamspace")

    """
    teamspace_id, asset_id = _find_ids(teamspace, folder)

    try:
        resp = client.client.build(FoldersApi).get_folder(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
        )
    except ApiException as exc:
        raise FoldersError("The folder retrieval request failed.") from exc
    else:
        return resp.data


def update_folder(
    folder: Union[Folder, Asset, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
    description: Optional[str] = None,
) -> None:
    """Update the mutable properties of a folder.

    The folder may be identified by asset id, path relative to
    a teamspace, or object representation (Folder or Asset instance).

    Presently, `description` is the only mutable property of a folder.

    Parameters
    ----------
    folder : Asset, Folder, or str
        The representation or string identifier of an existing folder.
    description : str, optional
        Description of the folder.
    teamspace : Teamspace or str, optional
        The representation or string identifier of the folder's
        teamspace. If the folder parameter is a Folder instance, the
        teamspace will be obtained from it.

    Returns
    -------
    None

    Raises
    ------
    FolderError
        If the folder cannot be updated.

    Examples
    --------
    >>> folders.update_folder(
    ...     "folder1",
    ...     teamspace="teamspace",
    ...     description="An updated description for folder one.",
    ... )

    """
    teamspace_id, asset_id = _find_ids(teamspace, folder)
    update_kwds = {}

    if description is not None:
        update_kwds.update(description=description)

    folder_update_request = FolderUpdateRequest(**update_kwds)

    try:
        client.client.build(FoldersApi).update_folder(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
            folder_update_request,
        )
    except ApiException as exc:
        raise FoldersError("The folder update request failed.") from exc


def delete_folder(
    folder: Union[Folder, Asset, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> None:
    """Delete a folder.

    The folder may be identified by asset id, path relative to
    a teamspace, or object representation (Folder or Asset instance).

    Parameters
    ----------
    folder : Asset, Folder, or str
        The representation or string identifier of an existing folder.
    teamspace : Teamspace or str, optional
        The representation or string identifier of the folder's
        teamspace. If the folder parameter is a Folder instance, the
        teamspace will be obtained from it.

    Returns
    -------
    None

    Raises
    ------
    FolderError
        If the folder cannot be deleted.

    Examples
    --------
    >>> folders.delete_folder(
    ...     "folder1",
    ...     teamspace="teamspace",
    ... )

    """
    teamspace_id, asset_id = _find_ids(teamspace, folder)

    try:
        client.client.build(FoldersApi).delete_folder(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
        )
    except ApiException as exc:
        raise FoldersError("The folder deletion request failed.") from exc


def list_folder_contents(
    folder: Union[Folder, Asset, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> list[Asset]:
    """Retrieve a list of assets in the folder.

    The folder may be identified by asset id, path relative to
    a teamspace, or object representation (Folder or Asset instance).

    Parameters
    ----------
    folder : Asset, Folder, or str
        The representation or string identifier of an existing folder.
    teamspace : Teamspace or str, optional
        The representation or string identifier of the folder's
        teamspace. If the folder parameter is a Folder instance, the
        teamspace will be obtained from it.

    Returns
    -------
    list of Assets.

    Raises
    ------
    FolderError
        If the folder's cannot be listed.

    Examples
    --------
    >>> assets = folders.list_folder_contents(
    ...     "folder1",
    ...     teamspace="teamspace"
    ... )
    >>> [asset.name for asset in assets]
    ["folder2"]

    """
    teamspace_id, asset_id = _find_ids(teamspace, folder)

    try:
        resp = client.client.build(FoldersApi).get_folder_contents(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
        )
    except ApiException as exc:
        raise FoldersError("The folder contents listing request failed.") from exc
    else:
        return resp.data


def add_assets(
    folder: Union[Folder, Asset, str],
    assets: list[Union[Asset, str]],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> None:
    """Move assets to a folder.

    The folder may be identified by asset id, path relative to
    a teamspace, or object representation (Folder or Asset instance).

    The assets may be identified by object representation or asset id.

    Parameters
    ----------
    folder : Asset, Folder, or str
        The representation or path of an existing folder.
    assets : list of Asset or str
        Assets to add to the folder.
    teamspace : Teamspace or str, optional
        The representation or string identifier of the folder's
        teamspace. If the folder parameter is a Folder instance, the
        teamspace will be obtained from it.

    Returns
    -------
    None.

    Raises
    ------
    FolderError
        If assets cannot be added to the folder.

    Examples
    --------
    >>> folder3 = folders.create_folder("folder3", teamspace="teamspace")
    >>> folders.add_assets(folder2, [folder3])
    >>> [asset.name for asset in folders.list_folder_contents(folder2)]
    ["folder3"]

    """
    teamspace_id, asset_id = _find_ids(teamspace, folder)
    members_to_add = [getattr(asset, "asset_id", asset) for asset in assets]

    try:
        client.client.build(FoldersApi).modify_folder_contents(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
            FoldersContentsModifyInner(
                members_to_add=members_to_add, members_to_remove=[]
            ),
        )
    except ApiException as exc:
        raise FoldersError("The folder contents update request failed.") from exc


def remove_assets(
    folder: Union[Folder, Asset, str],
    assets: list[Union[Asset, str]],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> None:
    """Remove assets from a folder.

    The folder may be identified by asset id, path relative to
    a teamspace, or object representation (Folder or Asset instance).

    The assets may be identified by object representation or asset id.

    Parameters
    ----------
    folder : Asset, Folder, or str
        The representation or string identifier of an existing folder.
    assets : list of Asset or str
        Assets to remove from the folder.
    teamspace : Teamspace or str, optional
        The representation or string identifier of the folder's
        teamspace. If the folder parameter is a Folder instance, the
        teamspace will be obtained from it.

    Returns
    -------
    None.

    Raises
    ------
    FolderError
        If assets cannot be removed from the folder.

    Examples
    --------
    >>> folders.remove_assets(folder2, [folder3])
    >>> [asset.name for asset in folders.list_folder_contents(folder2)]
    []

    """
    teamspace_id, asset_id = _find_ids(teamspace, folder)
    members_to_remove = [getattr(asset, "asset_id", asset) for asset in assets]

    try:
        client.client.build(FoldersApi).modify_folder_contents(
            client.get_workspace_id(),
            teamspace_id,
            asset_id,
            FoldersContentsModifyInner(
                members_to_add=[], members_to_remove=members_to_remove
            ),
        )
    except ApiException as exc:
        raise FoldersError("The folder contents update request failed.") from exc
