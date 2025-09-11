# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.task._base.builder import TaskBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerServer
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.task.flower_server_build.entity import TaskFlowerServerBuild
from digitalhub_runtime_flower.entities.task.flower_server_build.spec import (
    TaskSpecFlowerServerBuild,
    TaskValidatorFlowerServerBuild,
)
from digitalhub_runtime_flower.entities.task.flower_server_build.status import TaskStatusFlowerServerBuild


class TaskFlowerServerBuildBuilder(TaskBuilder, RuntimeEntityBuilderFlowerServer):
    """
    TaskFlowerServerBuild builder.
    """

    ENTITY_CLASS = TaskFlowerServerBuild
    ENTITY_SPEC_CLASS = TaskSpecFlowerServerBuild
    ENTITY_SPEC_VALIDATOR = TaskValidatorFlowerServerBuild
    ENTITY_STATUS_CLASS = TaskStatusFlowerServerBuild
    ENTITY_KIND = EntityKinds.TASK_FLOWER_SERVER_BUILD.value
