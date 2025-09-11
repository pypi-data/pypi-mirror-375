# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlower
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.run._base.entity import RunFlowerRun
from digitalhub_runtime_flower.entities.run._base.spec import RunSpecFlowerRun, RunValidatorFlowerRun
from digitalhub_runtime_flower.entities.run._base.status import RunStatusFlowerRun


class RunFlowerRunBuilder(RunBuilder, RuntimeEntityBuilderFlower):
    """
    RunFlowerRunBuilder runer.
    """

    ENTITY_CLASS = RunFlowerRun
    ENTITY_SPEC_CLASS = RunSpecFlowerRun
    ENTITY_SPEC_VALIDATOR = RunValidatorFlowerRun
    ENTITY_STATUS_CLASS = RunStatusFlowerRun
    ENTITY_KIND = EntityKinds.RUN_FLOWER.value
