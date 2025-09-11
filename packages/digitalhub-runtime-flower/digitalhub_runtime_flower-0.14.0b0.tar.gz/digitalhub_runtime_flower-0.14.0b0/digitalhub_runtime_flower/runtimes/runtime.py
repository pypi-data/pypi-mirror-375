# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Callable

from digitalhub.context.api import get_context
from digitalhub.runtimes._base import Runtime
from digitalhub.utils.logger import LOGGER

from digitalhub_runtime_flower.entities._commons.enums import Actions
from digitalhub_runtime_flower.utils.configuration import (
    collect_source,
    generate_pyproject_toml,
    prepare_run_parameters,
    prepare_toml_parameters,
)
from digitalhub_runtime_flower.utils.functions import run_simulation
from digitalhub_runtime_flower.utils.outputs import build_status


class RuntimeFlower(Runtime):
    """
    Runtime Flower class.
    """

    def build(self, function: dict, task: dict, run: dict) -> dict:
        """
        Build run spec.

        Parameters
        ----------
        function : dict
            The function.
        task : dict
            The task.
        run : dict
            The run.

        Returns
        -------
        dict
            The run spec.
        """
        return {
            **function.get("spec", {}),
            **task.get("spec", {}),
            **run.get("spec", {}),
        }

    def run(self, run: dict) -> dict:
        """
        Run function.

        Returns
        -------
        dict
            Status of the executed run.
        """
        raise NotImplementedError("Local execution not implemented for Flower runtime.")


class RuntimeFlowerApp(Runtime):
    """RuntimeFlowerApp class."""

    def __init__(self, project: str) -> None:
        super().__init__(project)

        ctx = get_context(self.project)
        self.runtime_dir = ctx.root / "runtime_flower"

        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        self._git_source: bool = False

    def build(self, function: dict, task: dict, run: dict) -> dict:
        """
        Build run spec.

        Parameters
        ----------
        function : dict
            The function.
        task : dict
            The task.
        run : dict
            The run.

        Returns
        -------
        dict
            The run spec.
        """
        return {
            **function.get("spec", {}),
            **task.get("spec", {}),
            **run.get("spec", {}),
        }

    def run(self, run: dict) -> dict:
        """
        Run function.

        Parameters
        ----------
        run : dict
            The run.

        Returns
        -------
        dict
            Status of the executed run.
        """
        LOGGER.info("Validating task.")
        action = self._validate_task(run)
        executable = self._get_executable(action)

        LOGGER.info("Starting task.")
        spec = run.get("spec")

        LOGGER.info("Configure execution.")
        run_args = self._configure_execution(spec["fab_source"], spec.get("parameters"))

        LOGGER.info("Executing run.")
        self._execute(executable, self.runtime_dir, run_args)

        LOGGER.info("Building status.")
        status = build_status(run["id"])

        LOGGER.info("Task completed, returning run status.")
        return status

    def _get_executable(self, action: Actions) -> Callable:
        """
        Get executable function based on action.

        Parameters
        ----------
        action : Actions
            The action to get the executable for.

        Returns
        -------
        Callable
            The executable function.
        """
        if Actions(action) == Actions.TRAIN:
            return run_simulation
        raise ValueError(f"Action {action} not supported.")

    def _configure_execution(self, fab_source: dict, parameters: dict | None = None) -> str:
        """
        Configure execution environment.

        Parameters
        ----------
        fab_source : dict
            The Flower Application source code.
        parameters : dict
            Additional parameters for configuration.

        Returns
        -------
        str
            The run arguments.
        """
        self._git_source = collect_source(self.runtime_dir, fab_source)

        if parameters is None:
            parameters = {}

        if not self._git_source:
            params = prepare_toml_parameters(parameters, fab_source)
            generate_pyproject_toml(self.runtime_dir, **params)
            return ""
        return prepare_run_parameters(parameters)

    def _collect_outputs(self, results: str) -> dict:
        """
        Collect outputs from execution.

        Parameters
        ----------
        results : dict
            The results from execution.

        Returns
        -------
        dict
            The collected outputs.
        """
        return results
