# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerApp
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.run.flower_app_train.entity import RunFlowerAppTrain
from digitalhub_runtime_flower.entities.run.flower_app_train.spec import (
    RunSpecFlowerAppTrain,
    RunValidatorFlowerAppTrain,
)
from digitalhub_runtime_flower.entities.run.flower_app_train.status import RunStatusFlowerAppTrain


class RunFlowerAppTrainBuilder(RunBuilder, RuntimeEntityBuilderFlowerApp):
    """
    RunFlowerAppTrain builder.
    """

    ENTITY_CLASS = RunFlowerAppTrain
    ENTITY_SPEC_CLASS = RunSpecFlowerAppTrain
    ENTITY_SPEC_VALIDATOR = RunValidatorFlowerAppTrain
    ENTITY_STATUS_CLASS = RunStatusFlowerAppTrain
    ENTITY_KIND = EntityKinds.RUN_FLOWER_APP_TRAIN.value
