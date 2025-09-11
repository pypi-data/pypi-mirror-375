# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from digitalhub.entities.task._base.spec import TaskSpecFunction, TaskValidatorFunction


class TaskSpecFlowerAppTrain(TaskSpecFunction):
    """
    TaskSpecFlowerAppTrain specifications.
    """

    def __init__(
        self,
        function: str,
        schedule: str | None = None,
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
            function=function,
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


class TaskValidatorFlowerAppTrain(TaskValidatorFunction):
    """
    TaskValidatorFlowerAppTrain validator.
    """

    schedule: Optional[str] = None
