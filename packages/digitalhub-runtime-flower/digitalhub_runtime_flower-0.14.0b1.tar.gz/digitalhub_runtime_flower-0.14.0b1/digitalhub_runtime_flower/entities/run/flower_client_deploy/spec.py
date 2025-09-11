# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from digitalhub_runtime_flower.entities.run._base.spec import RunSpecFlowerRun, RunValidatorFlowerRun


class RunSpecFlowerClientDeploy(RunSpecFlowerRun):
    """
    RunSpecFlowerClientDeploy specifications.
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
        image: str | None = None,
        base_image: str | None = None,
        requirements: list[str] | None = None,
        superlink: str | None = None,
        node_config: dict | None = None,
        root_certificates: str | None = None,
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
        self.image = image
        self.base_image = base_image
        self.requirements = requirements
        self.superlink = superlink
        self.node_config = node_config
        self.root_certificates = root_certificates


class RunValidatorFlowerClientDeploy(RunValidatorFlowerRun):
    """
    RunValidatorFlowerClientDeploy validator.
    """

    # Function parameters
    image: Optional[str] = None
    base_image: Optional[str] = None
    requirements: Optional[list[str]] = None

    # Run parameters
    superlink: Optional[str] = None
    """Flower superlink."""

    node_config: Optional[dict] = None
    """Node configuration."""

    root_certificates: Optional[str] = None
    """Root certificates."""
