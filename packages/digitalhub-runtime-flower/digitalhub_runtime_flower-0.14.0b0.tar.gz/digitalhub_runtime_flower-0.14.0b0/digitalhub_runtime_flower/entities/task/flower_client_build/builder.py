# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.task._base.builder import TaskBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerClient
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.task.flower_client_build.entity import TaskFlowerClientBuild
from digitalhub_runtime_flower.entities.task.flower_client_build.spec import (
    TaskSpecFlowerClientBuild,
    TaskValidatorFlowerClientBuild,
)
from digitalhub_runtime_flower.entities.task.flower_client_build.status import TaskStatusFlowerClientBuild


class TaskFlowerClientBuildBuilder(TaskBuilder, RuntimeEntityBuilderFlowerClient):
    """
    TaskFlowerClientBuild builder.
    """

    ENTITY_CLASS = TaskFlowerClientBuild
    ENTITY_SPEC_CLASS = TaskSpecFlowerClientBuild
    ENTITY_SPEC_VALIDATOR = TaskValidatorFlowerClientBuild
    ENTITY_STATUS_CLASS = TaskStatusFlowerClientBuild
    ENTITY_KIND = EntityKinds.TASK_FLOWER_CLIENT_BUILD.value
