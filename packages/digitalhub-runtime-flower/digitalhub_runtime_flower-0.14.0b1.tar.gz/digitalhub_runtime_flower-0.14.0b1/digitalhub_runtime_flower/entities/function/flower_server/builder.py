# SPDX-FileCopyrightText: © 2025 DSLab - Fondazione Bruno Kessler
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from digitalhub_runtime_flower.entities._base.runtime_entity.builder import RuntimeEntityBuilderFlowerServer
from digitalhub_runtime_flower.entities._commons.enums import EntityKinds
from digitalhub_runtime_flower.entities.function._base.builder import FunctionFlowerBuilder
from digitalhub_runtime_flower.entities.function.flower_server.entity import FunctionFlowerServer
from digitalhub_runtime_flower.entities.function.flower_server.spec import (
    FunctionSpecFlowerServer,
    FunctionValidatorFlowerServer,
)
from digitalhub_runtime_flower.entities.function.flower_server.status import FunctionStatusFlowerServer


class FunctionFlowerServerBuilder(FunctionFlowerBuilder, RuntimeEntityBuilderFlowerServer):
    """
    FunctionFlowerServer builder.
    """

    ENTITY_CLASS = FunctionFlowerServer
    ENTITY_SPEC_CLASS = FunctionSpecFlowerServer
    ENTITY_SPEC_VALIDATOR = FunctionValidatorFlowerServer
    ENTITY_STATUS_CLASS = FunctionStatusFlowerServer
    ENTITY_KIND = EntityKinds.FUNCTION_FLOWER_SERVER.value
