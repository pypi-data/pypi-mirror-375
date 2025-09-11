# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path
from typing import Any

from digitalhub.utils.generic_utils import decode_base64_string
from digitalhub.utils.git_utils import clone_repository
from digitalhub.utils.io_utils import write_text

##############################
# Source code collection
##############################


def collect_source(root: Path, fab_source: dict) -> bool:
    """
    Collect source files for Flower Application.

    Parameters
    ----------
    root : Path
        The runtime directory root.
    fab_source : dict
        The Flower Application source code.

    Returns
    -------
    bool
        True if the source is collected from a git repository, False otherwise.
    """
    source: str = fab_source.get("source")
    if source is not None:
        clone_repository(root, source.removeprefix("git+"))
        return True
    write_text(root / "client.py", decode_base64_string(fab_source.get("clientappbase64")))
    write_text(root / "server.py", decode_base64_string(fab_source.get("serverappbase64")))
    return False


##############################
# Parameters preparation
##############################


def _value_of(value: Any) -> str:
    """Return the typed value as string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def prepare_toml_parameters(
    parameters: dict[str, Any],
    fab_source: dict[str, str],
) -> dict:
    """
    Prepare parameters file for Flower Application.

    Parameters
    ----------
    parameters : dict[str, Any]
        The Flower Application parameters.
    server_app : str
        Local server application path.
    client_app : str
        Local client application path.

    Returns
    -------
    dict
        The prepared parameters.
    """
    params = {}
    params["name"] = parameters.pop("name", "flower-app")
    params["version"] = parameters.pop("version", "0.1.0")
    params["description"] = parameters.pop("description", "Flower Application")
    params["publisher"] = parameters.pop("publisher", "digitalhub-runtime-flower")
    params["dependencies"] = ", ".join([f'"{dep}"' for dep in parameters.pop("dependencies", [])])
    params["packages"] = ", ".join([f'"{pkg}"' for pkg in parameters.pop("packages", [])])
    params["server_app"] = fab_source.get("serverapp").split(":")[1]
    params["client_app"] = fab_source.get("clientapp").split(":")[1]

    # Configuration
    config_lines = []
    federation_config_lines = []
    for k, v in parameters.items():
        if k.startswith("options."):
            federation_config_lines.append(f"{k} = {_value_of(v)}")
        else:
            config_lines.append(f"{k} = {_value_of(v)}")

    if "options.num-supernodes" not in parameters:
        federation_config_lines.append("options.num-supernodes = 10")

    params["config"] = "\n".join(config_lines)
    params["federation_config"] = "\n".join(federation_config_lines)

    return params


def prepare_run_parameters(parameters: dict[str, Any]) -> str:
    """
    Prepare parameters for Flower Application.

    Parameters
    ----------
    parameters : dict[str, Any]
        The Flower Application parameters.

    Returns
    -------
    str
        The prepared parameters.
    """
    args = ""

    # Configuration
    config_lines = []
    for k, v in parameters.items():
        if k.startswith("options."):
            config_lines.append(f"--federation-config '{k}={v}'")
        else:
            config_lines.append(f"--run-config '{k}={v}'")

    if config_lines:
        args += " " + " ".join(config_lines)

    return args


##############################
# Template of pyproject.toml
##############################


def generate_pyproject_toml(
    root: Path,
    name: str,
    version: str,
    description: str,
    publisher: str,
    dependencies: str,
    packages: str,
    server_app: str,
    client_app: str,
    config: str,
    federation_config: str,
) -> None:
    """
    Generate pyproject.toml content for Flower Simulation.

    Parameters
    ----------
    root : Path
        The runtime directory root.
    name : str | None
        The application name.
    version : str | None
        The application version.
    description : str | None
        The application description.
    publisher : str | None
        The application publisher.
    dependencies : list[str] | None
        The application dependencies.
    packages : list[str] | None
        The application packages.
    server_app : str | None
        Local server application path.
    client_app : str | None
        Local client application path.
    config : dict[str, Any] | None
        The application configuration.
    federation_configs : dict[str, dict[str, Any]] | None
        The federations configuration.

    Returns
    -------
    None
    """
    pyproject = root / "pyproject.toml"
    toml_parts = "\n".join(
        [
            "[build-system]",
            'requires = ["hatchling"]',
            'build-backend = "hatchling.build"',
            "",
            "[project]",
            f'name = "{name}"',
            f'version = "{version}"',
            f'description = "{description}"',
            "dependencies = [",
            dependencies,
            "]",
            "",
            "[tool.hatch.build.targets.wheel]",
            f"packages = [{packages}]",
            "",
            "[tool.flwr.app]",
            f'publisher = "{publisher}"',
            "",
            "[tool.flwr.app.components]",
            f'serverapp = "server:{server_app}"',
            f'clientapp = "client:{client_app}"',
            "",
            "[tool.flwr.app.config]",
            config,
            "",
            "[tool.flwr.federations]",
            'default = "local-simulation"',
            "",
            "[tool.flwr.federations.local-simulation]",
            federation_config,
        ]
    )
    write_text(pyproject, toml_parts)
