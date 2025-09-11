# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing

from digitalhub.entities.task._base.entity import Task

if typing.TYPE_CHECKING:
    from digitalhub.entities._base.entity.metadata import Metadata

from digitalhub_runtime_flower.entities.task.flower_client_build.spec import TaskSpecFlowerClientBuild
from digitalhub_runtime_flower.entities.task.flower_client_build.status import TaskStatusFlowerClientBuild


class TaskFlowerClientBuild(Task):
    """
    TaskFlowerClientBuild class.
    """

    def __init__(
        self,
        project: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: TaskSpecFlowerClientBuild,
        status: TaskStatusFlowerClientBuild,
        user: str | None = None,
    ) -> None:
        super().__init__(project, uuid, kind, metadata, spec, status, user)

        self.spec: TaskSpecFlowerClientBuild
        self.status: TaskStatusFlowerClientBuild
