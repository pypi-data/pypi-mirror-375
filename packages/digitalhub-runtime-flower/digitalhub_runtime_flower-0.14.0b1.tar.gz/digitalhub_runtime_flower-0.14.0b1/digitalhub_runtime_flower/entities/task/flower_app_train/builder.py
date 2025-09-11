# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.task._base.builder import TaskBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerApp
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.task.flower_app_train.entity import TaskFlowerAppTrain
from digitalhub_runtime_flower.entities.task.flower_app_train.spec import (
    TaskSpecFlowerAppTrain,
    TaskValidatorFlowerAppTrain,
)
from digitalhub_runtime_flower.entities.task.flower_app_train.status import TaskStatusFlowerAppTrain


class TaskFlowerAppTrainBuilder(TaskBuilder, RuntimeEntityBuilderFlowerApp):
    """
    TaskFlowerAppTrain builder.
    """

    ENTITY_CLASS = TaskFlowerAppTrain
    ENTITY_SPEC_CLASS = TaskSpecFlowerAppTrain
    ENTITY_SPEC_VALIDATOR = TaskValidatorFlowerAppTrain
    ENTITY_STATUS_CLASS = TaskStatusFlowerAppTrain
    ENTITY_KIND = EntityKinds.TASK_FLOWER_APP_TRAIN.value
