# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from digitalhub_runtime_flower.entities.run._base.spec import RunSpecFlowerRun, RunValidatorFlowerRun


class RunSpecFlowerServerBuild(RunSpecFlowerRun):
    """
    RunSpecFlowerServerBuild specifications.
    """

    def __init__(
        self,
        task: str,
        local_execution: bool = False,
        function: str | None = None,
        workflow: str | None = None,
        node_selector: list[dict] | None = None,
        volumes: list[dict] | None = None,
        resources: dict | None = None,
        affinity: dict | None = None,
        tolerations: list[dict] | None = None,
        envs: list[dict] | None = None,
        secrets: list[str] | None = None,
        profile: str | None = None,
        runtime_class: str | None = None,
        priority_class: str | None = None,
        instructions: list[str] | None = None,
        image: str | None = None,
        base_image: str | None = None,
        requirements: list[str] | None = None,
        auth_public_keys: list[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            task=task,
            local_execution=local_execution,
            function=function,
            workflow=workflow,
            node_selector=node_selector,
            volumes=volumes,
            resources=resources,
            affinity=affinity,
            tolerations=tolerations,
            envs=envs,
            secrets=secrets,
            profile=profile,
            runtime_class=runtime_class,
            priority_class=priority_class,
            **kwargs,
        )
        self.instructions = instructions
        self.image = image
        self.base_image = base_image
        self.requirements = requirements
        self.auth_public_keys = auth_public_keys


class RunValidatorFlowerServerBuild(RunValidatorFlowerRun):
    """
    RunValidatorFlowerServerBuild validator.
    """

    # Task parameters
    instructions: Optional[list[str]] = None

    # Function parameters
    image: Optional[str] = None
    base_image: Optional[str] = None
    requirements: Optional[list[str]] = None

    # Run parameters
    auth_public_keys: Optional[list[str]] = None
    """Authentication public keys."""
