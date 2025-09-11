# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.spec import RunSpec, RunValidator


class RunSpecFlowerRun(RunSpec):
    """
    RunSpecFlowerRun specifications.
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


class RunValidatorFlowerRun(RunValidator):
    """
    RunValidatorFlowerRun validator.
    """
