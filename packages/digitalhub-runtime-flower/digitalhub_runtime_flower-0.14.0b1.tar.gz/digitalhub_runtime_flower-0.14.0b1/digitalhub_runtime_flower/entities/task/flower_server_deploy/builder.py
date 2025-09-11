# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.task._base.builder import TaskBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerServer
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.task.flower_server_deploy.entity import TaskFlowerServerDeploy
from digitalhub_runtime_flower.entities.task.flower_server_deploy.spec import (
    TaskSpecFlowerServerDeploy,
    TaskValidatorFlowerServerDeploy,
)
from digitalhub_runtime_flower.entities.task.flower_server_deploy.status import TaskStatusFlowerServerDeploy


class TaskFlowerServerDeployBuilder(TaskBuilder, RuntimeEntityBuilderFlowerServer):
    """
    TaskFlowerServerDeploy builder.
    """

    ENTITY_CLASS = TaskFlowerServerDeploy
    ENTITY_SPEC_CLASS = TaskSpecFlowerServerDeploy
    ENTITY_SPEC_VALIDATOR = TaskValidatorFlowerServerDeploy
    ENTITY_STATUS_CLASS = TaskStatusFlowerServerDeploy
    ENTITY_KIND = EntityKinds.TASK_FLOWER_SERVER_DEPLOY.value
