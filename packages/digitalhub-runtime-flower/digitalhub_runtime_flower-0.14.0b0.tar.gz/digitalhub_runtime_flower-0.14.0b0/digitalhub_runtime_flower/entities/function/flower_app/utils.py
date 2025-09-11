# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import typing
from pathlib import Path

from digitalhub.utils.exceptions import EntityError
from digitalhub.utils.file_utils import eval_py_type
from digitalhub.utils.generic_utils import encode_source
from digitalhub.utils.uri_utils import has_git_scheme, has_local_scheme

if typing.TYPE_CHECKING:
    from digitalhub_runtime_flower.entities.function.flower_app.entity import FunctionFlowerApp


def source_check(**kwargs) -> dict:
    """
    Check source code.

    Parameters
    ----------
    **kwargs
        Keyword arguments.

    Returns
    -------
    dict
        Checked source.
    """
    fab_source: dict = kwargs.pop("fab_source", None)
    source: str = kwargs.pop("source", None)
    clientapp: str = kwargs.pop("clientapp", None)
    serverapp: str = kwargs.pop("serverapp", None)
    clientbase64: str = kwargs.pop("clientbase64", None)
    serverbase64: str = kwargs.pop("serverbase64", None)

    if fab_source is not None:
        source = fab_source.get("source")
        clientapp = fab_source.get("clientapp")
        serverapp = fab_source.get("serverapp")
        clientbase64 = fab_source.get("clientbase64")
        serverbase64 = fab_source.get("serverbase64")

    kwargs["fab_source"] = _check_params(
        source=source,
        clientapp=clientapp,
        serverapp=serverapp,
        clientbase64=clientbase64,
        serverbase64=serverbase64,
    )
    return kwargs


def _check_params(
    source: str | None = None,
    clientapp: str | None = None,
    serverapp: str | None = None,
    clientbase64: str | None = None,
    serverbase64: str | None = None,
) -> dict:
    """
    Check source code.

    Parameters
    ----------
    source : str | None
        Github repository URL.
    clientapp : str | None
        Local client application path.
    serverapp : str | None
        Local server application path.
    clientbase64 : str | None
        Client application base64.
    serverbase64 : str | None
        Server application base64.

    Returns
    -------
    dict
        Checked source.
    """
    fab_source = {}

    if source is not None:
        fab_source["source"] = source

    if clientapp is not None:
        fab_source["clientapp"] = clientapp

    if serverapp is not None:
        fab_source["serverapp"] = serverapp

    if clientbase64 is not None:
        fab_source["clientbase64"] = clientbase64

    if serverbase64 is not None:
        fab_source["serverbase64"] = serverbase64

    return fab_source


def source_post_check(exec: FunctionFlowerApp) -> FunctionFlowerApp:
    """
    Post check source.

    Parameters
    ----------
    exec : FunctionFlowerApp
        Executable.

    Returns
    -------
    FunctionFlowerApp
        Updated executable.
    """
    if exec.spec.fab_source is None:
        return exec

    git_source = exec.spec.fab_source.get("source", None)
    if git_source is not None:
        if not has_git_scheme(git_source):
            raise EntityError("Source must be a valid git URL.")
        return exec

    clientappbase64 = exec.spec.fab_source.get("clientbase64", None)
    serverappbase64 = exec.spec.fab_source.get("serverbase64", None)

    clientapp = exec.spec.fab_source.get("clientapp", None)
    serverapp = exec.spec.fab_source.get("serverapp", None)
    if clientapp is None or serverapp is None:
        raise EntityError("Either source or both clientapp and serverapp must be provided.")

    clientapp = _validate_handler(clientapp)
    serverapp = _validate_handler(serverapp)

    if clientappbase64 is not None and serverappbase64 is not None:
        return exec

    # Encode clientapp and serverapp

    try:
        clientapp_path = _parse_local_app(clientapp)
        if has_local_scheme(clientapp_path) and Path(clientapp_path).is_file():
            exec.spec.fab_source["clientappbase64"] = encode_source(clientapp_path)

        serverapp_path = _parse_local_app(serverapp)
        if has_local_scheme(serverapp_path) and Path(serverapp_path).is_file():
            exec.spec.fab_source["serverappbase64"] = encode_source(serverapp_path)

    except Exception as e:
        raise EntityError(f"Error encoding source: {e}")

    return exec


def _parse_local_app(handler: str) -> str:
    """
    Parse local app.

    Parameters
    ----------
    handler : str
        Handler.

    Returns
    -------
    str
        Parsed handler.
    """
    return handler.split(":")[0].replace(".", os.sep) + ".py"


def _validate_handler(handler: str) -> None:
    """
    Validate handler.

    Parameters
    ----------
    handler : str
        Handler.

    Returns
    -------
    None
    """
    if not isinstance(handler, str):
        raise EntityError("Handler must be a string.")
    if ":" not in handler or len(handler.split(":")) != 2:
        raise EntityError("Handler must be in the form 'module.path:callable'.")
    if not eval_py_type(handler.split(":")[0].replace(".", os.sep) + ".py"):
        raise EntityError("Handler must be a valid Python file.")
    return handler
