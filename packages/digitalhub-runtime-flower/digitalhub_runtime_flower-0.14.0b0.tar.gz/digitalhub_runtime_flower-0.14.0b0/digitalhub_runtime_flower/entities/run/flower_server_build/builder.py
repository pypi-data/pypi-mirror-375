# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub.entities.run._base.builder import RunBuilder

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerServer
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.run.flower_server_build.entity import RunFlowerServerBuild
from digitalhub_runtime_flower.entities.run.flower_server_build.spec import (
    RunSpecFlowerServerBuild,
    RunValidatorFlowerServerBuild,
)
from digitalhub_runtime_flower.entities.run.flower_server_build.status import RunStatusFlowerServerBuild


class RunFlowerServerBuildBuilder(RunBuilder, RuntimeEntityBuilderFlowerServer):
    """
    RunFlowerServerBuild builder.
    """

    ENTITY_CLASS = RunFlowerServerBuild
    ENTITY_SPEC_CLASS = RunSpecFlowerServerBuild
    ENTITY_SPEC_VALIDATOR = RunValidatorFlowerServerBuild
    ENTITY_STATUS_CLASS = RunStatusFlowerServerBuild
    ENTITY_KIND = EntityKinds.RUN_FLOWER_SERVER_BUILD.value
