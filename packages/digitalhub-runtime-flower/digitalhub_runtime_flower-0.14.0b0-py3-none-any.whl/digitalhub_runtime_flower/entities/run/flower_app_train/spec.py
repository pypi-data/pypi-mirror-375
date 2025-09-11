# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from digitalhub_runtime_flower.entities.run._base.spec import RunSpecFlowerRun, RunValidatorFlowerRun


class RunSpecFlowerAppTrain(RunSpecFlowerRun):
    """
    RunSpecFlowerAppTrain specifications.
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
        schedule: str | None = None,
        fab_source: dict | None = None,
        image: str | None = None,
        base_image: str | None = None,
        requirements: list[str] | None = None,
        parameters: dict | None = None,
        federation: str | None = None,
        superlink: str | None = None,
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
        self.schedule = schedule
        self.fab_source = fab_source
        self.image = image
        self.base_image = base_image
        self.requirements = requirements
        self.parameters = parameters
        self.federation = federation
        self.superlink = superlink
        self.root_certificates = root_certificates


class RunValidatorFlowerAppTrain(RunValidatorFlowerRun):
    """
    RunValidatorFlowerAppTrain validator.
    """

    # Task parameters
    schedule: Optional[str] = None

    # Function parameters
    fab_source: Optional[dict] = None
    image: Optional[str] = None
    base_image: Optional[str] = None
    requirements: Optional[list[str]] = None

    # Run parameters
    parameters: Optional[dict] = None
    """Run parameters."""

    federation: Optional[str] = None
    """Flower federation."""

    superlink: Optional[str] = None
    """Flower superlink."""

    root_certificates: Optional[str] = None
    """Root certificates."""
